SELECT
    strftime('%Y', t.date) AS year,
    t.lake,
    r.place,
    r.weight
FROM tournaments t
JOIN results r ON t.id = r.tournament_id
WHERE r.place IN (1, 2, 3)
  AND r.weight IS NOT NULL
GROUP BY year, t.lake, r.place
ORDER BY year DESC, t.lake, r.place;
