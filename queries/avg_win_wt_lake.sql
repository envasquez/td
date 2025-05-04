SELECT
    t.lake,
    r.place,
    COUNT(*) AS tournament_count,
    ROUND(AVG(r.weight), 2) AS avg_winning_weight
FROM tournaments t
JOIN results r ON t.id = r.tournament_id
WHERE r.place in (1, 2, 3) AND t.lake IS NOT NULL
GROUP BY t.lake