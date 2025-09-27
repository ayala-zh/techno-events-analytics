-- 1. Top 10 most favorited artists
SELECT a.id, a.name, COUNT(fa.id) AS favorites
FROM favoriteartists fa
JOIN artists a ON fa.artist_id = a.id
GROUP BY a.id, a.name
ORDER BY favorites DESC
LIMIT 10;

-- 2. Most active users by events attended
SELECT u.id, u.username, COUNT(eh.id) AS attended
FROM eventhistory eh
JOIN users u ON eh.user_id = u.id
WHERE eh.has_attended = true
GROUP BY u.id, u.username
ORDER BY attended DESC;

-- 3. Average event rating by country
SELECT c.name AS country, ROUND(AVG(eh.rate), 2) AS avg_rating
FROM eventhistory eh
JOIN events e ON eh.event_id = e.id
JOIN locations l ON e.location_id = l.id
JOIN countries c ON l.country_id = c.id
WHERE eh.rate IS NOT NULL
GROUP BY c.name
ORDER BY avg_rating DESC;

-- 4. Attendance by day of the week
SELECT TO_CHAR(e.date, 'Day') AS day_of_week,
       COUNT(eh.id) FILTER (WHERE eh.has_attended = true) AS total_attendances,
       COUNT(DISTINCT eh.user_id) FILTER (WHERE eh.has_attended = true) AS unique_attendees
FROM events e
LEFT JOIN eventhistory eh ON eh.event_id = e.id
GROUP BY TO_CHAR(e.date, 'Day'), EXTRACT(DOW FROM e.date)
ORDER BY EXTRACT(DOW FROM e.date);

-- 5. Top venues by event count + average rating + total attendance
SELECT 
    e.venue,
    COUNT(e.id) AS events_count,
    COALESCE(ROUND(AVG(eh.rate), 2), 0) AS avg_rating,
    COUNT(CASE WHEN eh.has_attended THEN 1 END) AS total_attendance
FROM events e
LEFT JOIN eventhistory eh ON e.id = eh.event_id
GROUP BY e.venue
ORDER BY events_count DESC, avg_rating DESC;


-- 6. Most popular genre overall (by attendance)
SELECT g.name, COUNT(*) AS attendances
FROM eventhistory eh
JOIN events e ON eh.event_id = e.id
JOIN genres g ON e.genre_id = g.id
WHERE eh.has_attended = true
GROUP BY g.name
ORDER BY attendances DESC;

-- 7. Most engaging events (based on interest + attendance)
SELECT e.id,
       e.name AS event_name,
       COUNT(CASE WHEN eh.is_interested THEN 1 END) AS total_interested,
       COUNT(CASE WHEN eh.has_attended THEN 1 END) AS total_attended,
       (COUNT(CASE WHEN eh.is_interested THEN 1 END) + COUNT(CASE WHEN eh.has_attended THEN 1 END)) AS total_engagement
FROM events e
LEFT JOIN eventhistory eh ON e.id = eh.event_id
GROUP BY e.id, e.name
ORDER BY total_engagement DESC
LIMIT 10;


-- 8. Highest impact events (rating × attendance)
WITH event_stats AS (
  SELECT e.id,
         e.name,
         COUNT(CASE WHEN eh.has_attended THEN 1 END) AS total_attended,
         AVG(eh.rate) AS avg_rating
  FROM events e
  LEFT JOIN eventhistory eh ON e.id = eh.event_id
  WHERE eh.rate IS NOT NULL
  GROUP BY e.id, e.name
)
SELECT id,
       name,
       total_attended,
       ROUND(avg_rating, 2) AS avg_rating,
       (total_attended * avg_rating) AS impact_score
FROM event_stats
WHERE total_attended > 0
ORDER BY impact_score DESC
LIMIT 10;

-- 9. Artists with the most performances
SELECT a.id, a.name, COUNT(ea.id) AS performances
FROM eventartists ea
JOIN artists a ON ea.artist_id = a.id
GROUP BY a.id, a.name
ORDER BY performances DESC
LIMIT 20;

-- 10. User genre preference distribution (top 10 genres)
SELECT g.name, COUNT(fg.id) AS users_preferring
FROM favoritegenres fg
JOIN genres g ON fg.genre_id = g.id
GROUP BY g.name
ORDER BY users_preferring DESC
LIMIT 10;