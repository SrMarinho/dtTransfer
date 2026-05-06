select
    EMPRESA,
    PRODUTO,
    DEMANDA_DIA_PONDERADA_ORIGINAL,
    DEMANDA_DIA_PONDERADA,
    MES,
    ANO,
    FORMAT (GETDATE (), 'yyyy-MM-dd') as DATA
from
    DEMANDA_RUPTURA
where
    MES = FORMAT (GETDATE (), 'MM')
    and ANO = FORMAT (GETDATE (), 'yyyy')
