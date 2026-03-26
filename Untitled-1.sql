-- MySQL 8+ query (window functions + recursive CTEs)
-- Produces DST-aligned 6-hour feature snapshots with:
--   - duration-based TIR (tir_seconds)
--   - coverage_seconds (quality_flag=1 overlap duration)
--   - tie_rate = tir_seconds / coverage_seconds
-- Late-arrival safety ("as-of"): only use readings ingested at/before :asof_ts_utc.
--
-- Parameters (bind in your app):
--   :patient_id
--   :device_id
--   :asof_ts_utc                 (snapshot cutoff; require :window_end_utc <= :asof_ts_utc)
--   :window_start_utc, :window_end_utc  (UTC window; end is exclusive)
--   :tir_low, :tir_high         (e.g., 70 and 180 mg/dL)
--
-- Prereq:
--   - patients.timezone holds IANA TZ names (e.g. 'America/New_York')
--   - MySQL timezone tables loaded for CONVERT_TZ()

WITH RECURSIVE
patient_tz AS (
  SELECT p.timezone AS tz_name
  FROM patients p
  WHERE p.patient_id = :patient_id
),
bounds AS (
  SELECT
    pt.tz_name,
    CONVERT_TZ(:window_start_utc, '+00:00', pt.tz_name) AS window_start_local,
    CONVERT_TZ(:window_end_utc,   '+00:00', pt.tz_name) AS window_end_local
  FROM patient_tz pt
),
bucket_seed AS (
  -- Floor window_start_local to the previous local 6-hour boundary.
  SELECT
    b.tz_name,
    TIMESTAMP(
      DATE(b.window_start_local),
      MAKETIME(
        HOUR(b.window_start_local) - MOD(HOUR(b.window_start_local), 6),
        0,
        0
      )
    ) AS bucket_start_local
  FROM bounds b
),
buckets_local AS (
  SELECT
    bs.tz_name,
    bs.bucket_start_local
  FROM bucket_seed bs

  UNION ALL

  SELECT
    bl.tz_name,
    bl.bucket_start_local + INTERVAL 6 HOUR
  FROM buckets_local bl
  JOIN bounds b ON 1=1
  WHERE bl.bucket_start_local + INTERVAL 6 HOUR <= b.window_end_local
),
buckets_utc AS (
  SELECT
    bl.bucket_start_local,
    bl.tz_name,
    CONVERT_TZ(bl.bucket_start_local, bl.tz_name, '+00:00') AS bucket_start_utc,
    CONVERT_TZ(bl.bucket_start_local + INTERVAL 6 HOUR, bl.tz_name, '+00:00') AS bucket_end_utc
  FROM buckets_local bl
),

-- Only readings ingested at/before :asof_ts_utc (late-arrival safe).
asof_pool AS (
  SELECT
    r.patient_id,
    r.device_id,
    r.measured_at_utc,
    r.value_mgdl,
    r.quality_flag,
    r.ingest_ts_utc
  FROM cgm_readings r
  WHERE r.patient_id = :patient_id
    AND r.device_id  = :device_id
    AND r.ingest_ts_utc <= :asof_ts_utc
    AND r.measured_at_utc < :window_end_utc
),

-- Add the last reading just before the window so the first bucket
-- gets a proper "segment" covering from window_start_utc onward.
last_before AS (
  SELECT
    ap.patient_id, ap.device_id, ap.measured_at_utc, ap.value_mgdl, ap.quality_flag, ap.ingest_ts_utc
  FROM asof_pool ap
  WHERE ap.measured_at_utc < :window_start_utc
  ORDER BY ap.measured_at_utc DESC
  LIMIT 1
),

in_window AS (
  SELECT *
  FROM asof_pool
  WHERE measured_at_utc >= :window_start_utc
    AND measured_at_utc <  :window_end_utc
),

asof_readings AS (
  SELECT * FROM in_window
  UNION ALL
  SELECT * FROM last_before
),

ordered AS (
  SELECT
    ar.patient_id,
    ar.device_id,
    ar.measured_at_utc,
    ar.value_mgdl,
    ar.quality_flag,
    LEAD(ar.measured_at_utc) OVER (
      PARTITION BY ar.device_id
      ORDER BY ar.measured_at_utc
    ) AS next_measured_at_utc
  FROM asof_readings ar
),

bucket_segments AS (
  -- Each reading step covers [measured_at_utc, next_measured_at_utc).
  -- We overlap each step with each DST-aligned 6-hour bucket.
  SELECT
    b.bucket_start_utc,
    b.bucket_end_utc,
    o.value_mgdl,
    o.quality_flag,

    GREATEST(o.measured_at_utc, b.bucket_start_utc) AS overlap_start_utc,
    LEAST(
      COALESCE(o.next_measured_at_utc, b.bucket_end_utc),
      b.bucket_end_utc
    ) AS overlap_end_utc
  FROM buckets_utc b
  JOIN ordered o
    ON o.measured_at_utc < b.bucket_end_utc
   AND COALESCE(o.next_measured_at_utc, b.bucket_end_utc) > b.bucket_start_utc
),

bucket_durations AS (
  SELECT
    bs.bucket_start_utc,
    bs.bucket_end_utc,

    CASE
      WHEN bs.overlap_end_utc > bs.overlap_start_utc AND bs.quality_flag = 1
      THEN TIMESTAMPDIFF(SECOND, bs.overlap_start_utc, bs.overlap_end_utc)
      ELSE 0
    END AS coverage_seconds,

    CASE
      WHEN bs.overlap_end_utc > bs.overlap_start_utc
       AND bs.quality_flag = 1
       AND bs.value_mgdl >= :tir_low
       AND bs.value_mgdl <= :tir_high
      THEN TIMESTAMPDIFF(SECOND, bs.overlap_start_utc, bs.overlap_end_utc)
      ELSE 0
    END AS tir_seconds,

    CASE
      WHEN bs.overlap_end_utc > bs.overlap_start_utc AND bs.quality_flag = 1
      THEN TIMESTAMPDIFF(SECOND, bs.overlap_start_utc, bs.overlap_end_utc)
      ELSE 0
    END AS quality_seconds,

    bs.value_mgdl
  FROM bucket_segments bs
),

agg_mean AS (
  -- Duration-weighted mean glucose over quality-good overlap.
  SELECT
    bd.bucket_start_utc,
    MAX(bd.bucket_end_utc) AS bucket_end_utc,

    SUM(bd.coverage_seconds) AS coverage_seconds,
    SUM(bd.tir_seconds) AS tir_seconds,

    CASE
      WHEN SUM(bd.quality_seconds) > 0
      THEN SUM(bd.quality_seconds * bd.value_mgdl) / SUM(bd.quality_seconds)
      ELSE NULL
    END AS glucose_mean_mgdl
  FROM bucket_durations bd
  GROUP BY bd.bucket_start_utc
),

agg_var AS (
  -- Duration-weighted (population) variance using the computed mean.
  SELECT
    bd.bucket_start_utc,
    am.bucket_end_utc,
    am.coverage_seconds,
    am.tir_seconds,
    am.glucose_mean_mgdl,

    CASE
      WHEN am.coverage_seconds > 0
      THEN SUM(
        bd.quality_seconds * POW(bd.value_mgdl - am.glucose_mean_mgdl, 2)
      ) / am.coverage_seconds
      ELSE NULL
    END AS glucose_var_mgdl
  FROM bucket_durations bd
  JOIN agg_mean am
    ON am.bucket_start_utc = bd.bucket_start_utc
  GROUP BY
    bd.bucket_start_utc,
    am.bucket_end_utc,
    am.coverage_seconds,
    am.tir_seconds,
    am.glucose_mean_mgdl
)

SELECT
  :patient_id AS patient_id,
  :device_id  AS device_id,
  :asof_ts_utc AS asof_ts_utc,

  av.bucket_start_utc,
  av.bucket_end_utc,

  av.coverage_seconds,
  av.tir_seconds,
  av.tir_seconds / NULLIF(av.coverage_seconds, 0) AS tie_rate,

  av.glucose_mean_mgdl,
  SQRT(av.glucose_var_mgdl) AS glucose_std_mgdl
FROM agg_var av
ORDER BY av.bucket_start_utc;
