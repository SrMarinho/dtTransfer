SELECT A.NF_NUMERO               AS nf_numero,
       A.EMPRESA                 AS empresa,
       CAST(A.MOVIMENTO AS DATE) AS movimento,
       A.JUSTIFICATIVA           AS justificativa,
       A.ID_NOTA                 AS id_nota
    FROM CANCELAMENTOS_NOTAS_FISCAIS A WITH(NOLOCK)
WHERE 
    CAST(A.MOVIMENTO AS DATE) = 'REPLACE_START_DATE'
