SELECT strftime('%Y', t.date) AS year, r.place, ROUND(AVG(r.weight), 2) AS avg_weight
FROM results r
JOIN tournaments t ON r.tournament_id = t.id
WHERE r.place IN (1, 2, 3) AND r.weight IS NOT NULL
GROUP BY year, place