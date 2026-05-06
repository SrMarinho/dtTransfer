-- Extração para a entidade sample
-- Use REPLACE_START_DATE / REPLACE_END_DATE para incremental.
SELECT
    id,
    nome
FROM sample
WHERE 1=1
