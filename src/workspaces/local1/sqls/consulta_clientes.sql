-- Extração para a entidade clientes
-- Use REPLACE_START_DATE / REPLACE_END_DATE para incremental.
SELECT
    id,
    nome
FROM clientes
WHERE 1=1
