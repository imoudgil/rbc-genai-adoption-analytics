-- Enterprise GenAI adoption questions (SQLite stand-in for SQL Server / Postgres)

-- 1) License vs activate vs weekly active (adoption funnel)
SELECT
  u.business_unit,
  COUNT(*) AS licensed_users,
  SUM(CASE WHEN e.user_id IS NOT NULL THEN 1 ELSE 0 END) AS activated_users,
  ROUND(100.0 * SUM(CASE WHEN e.user_id IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS activation_pct
FROM users u
LEFT JOIN (
  SELECT DISTINCT user_id FROM events
) e ON e.user_id = u.user_id
GROUP BY u.business_unit
ORDER BY activation_pct ASC;

-- 2) Weekly active users and value events (usage vs value)
SELECT
  strftime('%Y-%W', e.event_date) AS year_week,
  MIN(e.event_date) AS week_start,
  COUNT(DISTINCT e.user_id) AS wau,
  SUM(e.is_value_event) AS value_events,
  COUNT(*) AS sessions
FROM events e
GROUP BY year_week
ORDER BY year_week;

-- 3) Feature mix: sessions vs value (draft vanity)
SELECT
  f.feature_name,
  COUNT(*) AS sessions,
  SUM(e.is_value_event) AS value_events,
  ROUND(100.0 * SUM(e.is_value_event) / COUNT(*), 1) AS value_rate_pct
FROM events e
JOIN features f ON f.feature_id = e.feature
GROUP BY f.feature_name
ORDER BY value_rate_pct ASC;

-- 4) Time-to-first-value by business unit (days from license)
SELECT
  u.business_unit,
  ROUND(AVG(julianday(first_value.first_value_date) - julianday(u.licensed_on)), 1) AS mean_ttv_days,
  COUNT(*) AS users_with_value
FROM users u
JOIN (
  SELECT user_id, MIN(event_date) AS first_value_date
  FROM events
  WHERE is_value_event = 1
  GROUP BY user_id
) first_value ON first_value.user_id = u.user_id
GROUP BY u.business_unit
ORDER BY mean_ttv_days DESC;

-- 5) Shadow IT signal: copy-to-external by BU
SELECT
  u.business_unit,
  ROUND(100.0 * AVG(e.copied_to_external), 1) AS pct_sessions_copied_external
FROM events e
JOIN users u ON u.user_id = e.user_id
GROUP BY u.business_unit
ORDER BY pct_sessions_copied_external DESC;

-- 6) Repeat use: users with a value event in week 2+ after first value
SELECT
  u.business_unit,
  COUNT(*) AS valued_users,
  SUM(CASE WHEN r.repeat_user = 1 THEN 1 ELSE 0 END) AS repeat_users,
  ROUND(100.0 * AVG(r.repeat_user), 1) AS repeat_pct
FROM users u
JOIN (
  SELECT
    user_id,
    MIN(event_date) AS first_value_date
  FROM events
  WHERE is_value_event = 1
  GROUP BY user_id
) fv ON fv.user_id = u.user_id
JOIN (
  SELECT
    e.user_id,
    MAX(CASE WHEN julianday(e.event_date) >= julianday(fv.first_value_date) + 7
             AND e.is_value_event = 1 THEN 1 ELSE 0 END) AS repeat_user
  FROM events e
  JOIN (
    SELECT user_id, MIN(event_date) AS first_value_date
    FROM events
    WHERE is_value_event = 1
    GROUP BY user_id
  ) fv ON fv.user_id = e.user_id
  GROUP BY e.user_id
) r ON r.user_id = u.user_id
GROUP BY u.business_unit
ORDER BY repeat_pct ASC;
