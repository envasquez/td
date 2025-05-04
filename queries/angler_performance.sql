SELECT
    t.date,
    strftime('%Y', t.date) AS year,
    t.lake,
    r.place,
    r.weight,
    r.fish,
    r.big_bass,
    prize
FROM tournaments t
JOIN results r ON r.tournament_id = t.id
WHERE
    LOWER(r.angler1) LIKE ?
    OR LOWER(r.angler2) LIKE ?
ORDER BY r.place ASC, t.date DESC
