select
    EMPRESA AS id_empresa,
    PRODUTO AS id_produto,
    FORMAT (GETDATE (), 'yyyy-MM-dd') AS dt_referencia,
    CAST(ESTOQUE_MINIMO as int) AS estoque_minimo,
    CAST(ROUND((ESTOQUE_MINIMO / 30), 2) as float) AS estoque_minimo_dia,
    VALIDADE_MINIMO AS validade_min
from
    PRODUTOS_PARAMETROS_EMPRESAS
WITH
    (NOLOCK)
where
    VALIDADE_MINIMO >= GETDATE ()