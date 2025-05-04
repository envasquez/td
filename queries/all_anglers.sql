SELECT DISTINCT angler FROM (
    SELECT angler1 AS angler FROM results
    UNION
    SELECT angler2 AS angler FROM results
) WHERE angler IS NOT NULL AND angler != ''
ORDER BY angler
