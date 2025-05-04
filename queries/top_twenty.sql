            SELECT
                place,
                angler1,
                angler2,
                fish,
                big_bass,
                weight,
                prize
            FROM results
            WHERE tournament_id = ?
            ORDER BY place ASC
            LIMIT 20