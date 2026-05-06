SELECT
    DISTINCT tns.CODTNS,
    tns.DESTNS,
    t.CODEMP as EMPRESA,
    t.CODFIL AS FILIAL_ERP,
    fi.SIGFIL as NOME_FILIAL,
    m.SEQMOV AS SEQ_MOV,
    fi.USU_UNINEG AS FILIAL_LINX,
    fi.CIDFIL as CIDADE,
    fi.SIGUFS as UF,
    COALESCE (rt.CODCCU, '0') as COD_CC_RATEIO_TITULO,
    COALESCE (crt.DESCCU, 'sem centro_custo') as DESCR_CC_RATEIO,
    COALESCE (rt.CTARED, 0) AS COD_CONTABIL_RAT_TITULO,
    COALESCE (pct.DESCTA, 'sem conta contábil') AS desc_conta_contabil_rateio_titulo,
    t.DATEMI AS DATA_EMISSAO_TITULO,
    t.NUMNFC as NF_ENTRADA_TITULO,
    t.SNFNFC as SERIE_NF_ENTRADA_TITULO,
    t.VCTORI as VCTO_ORIGINAL,
    t.VCTPRO as VENCIMENTO,
    t.ULTPGT as ULT_PAGTO,
    m.DATPGT AS DATA_PAGAMENTO,
    m.CODFPG as cod_FORMA_PGTO,
    COALESCE (fp.DESFPG, 'sem forma de pagamento') AS des_forma_pgto,
    T.SITTIT AS SITUACAO_TITULO,
    t.NUMTIT as TITULO,
    t.CODTPT as TIPO_TPT,
    tt.DESTPT AS des_tipo,
    fp.DESFPG AS des_tipo_fpg,
    t.CODFOR as COD_FORN,
    fo.NOMFOR as NOME_FORN,
    fo.APEFOR AS NOME_FANTASIA_FORN,
    fo.CGCCPF as CPNJ_CPF,
    t.FILNFV as FILIAL_NFS,
    t.SNFNFV as SERIE_NFS,
    t.NUMNFV as NF_SAIDA,
    rt.VLRRAT AS VALOR_RATEIO,
    rt.VLRCTA,
    m.VLRIRF as IRRF,
    m.VLRISS as ISS,
    m.VLRINS as INSS,
    m.VLRPIS as PIS,
    m.VLRCOF as COFINS,
    m.VLRCSL as CSLL,
    m.ORIIRF as OUTRAS_RETENCOES,
    t.VLRORI as TOTAL,
    t.VLRABE as VALOR_ABERTO,
    t.OBSTCP as OBSERVACAO,
    m.VLRJRS as VALOR_JUROS,
    m.VLRMUL as VALOR_MULTA,
    m.VLRENC as VALOR_ENCARGO,
    m.VLROAC as VALOR_ACRESCIMO,
    m.VLRDSC as VALOR_DESCONTO,
    m.VLRODE as VALOR_OUTROS_DESCONTOS,
    COALESCE (oc.NUMOCP, 0) AS NUM_ORDEM_COMPRA,
    nfp.NUMNFC AS NUM_NOTA_FISCAL,
    oc.DATEMI AS DATA_EMISSAO,
    nfp.SEQIPO AS SEQ_PRODUTO,
    nfp.CODPRO AS CODIGO_PRODUTO,
    nfp.CPLIPC AS DESCRICAO_PRODUTO,
    COALESCE (oc.OBSOCP, 'sem observação na ordem de compra') AS OBSERVACAO_ORDEM_COMPRA,
    COALESCE (oc.USUGER, 0) AS COD_USUARIO_GERACAO_ORDEM_COMPRA,
    uoc.NOMUSU AS NOME_USUARIO_GERACAO,
    COALESCE (aoc.USUAPR, 0) AS COD_USUARIO_APROVADOR_OC,
    COALESCE (uaoc.NOMUSU, 'sem aprovador') AS NOME_USUARIO_APROVADOR_OC,
    COALESCE (aoc.NIVAPR, 0) AS NIVEL_USUARIO_OC,
    'Produto' AS tipo,
    CASE
        WHEN oc.SITOCP IS NULL THEN 'Sem ordem de Compra'
        WHEN oc.sitocp = 1 THEN 'Aberto total'
        WHEN oc.sitocp = 2 THEN 'Aberto parcial'
        WHEN oc.sitocp = 3 THEN 'Suspenso'
        WHEN oc.sitocp = 4 THEN 'Liquidado'
        WHEN oc.sitocp = 5 THEN 'Cancelado'
        WHEN oc.sitocp = 6 THEN 'Aguardando integração WMS'
        WHEN oc.sitocp = 7 THEN 'Em transmissão'
        WHEN oc.sitocp = 8 THEN 'Preparação Analise ou NF'
        WHEN oc.sitocp = 9 THEN 'Não fechado'
        ELSE 'Sem ordem de Compra'
    END AS SITUACAO_ORDEM_COMPRA,
    t.DATENT AS data_entrada
FROM
    SAPIENS_PROD.E002TPT tt,
    (
        SAPIENS_PROD.E501TCP t
        LEFT OUTER JOIN SAPIENS_PROD.E066FPG fp ON fp.CODEMP = t.CODEMP
        AND fp.CODFPG = t.CODFPG
        LEFT OUTER JOIN SAPIENS_PROD.E440IPC nfp ON nfp.CODEMP = t.CODEMP
        AND nfp.CODFIL = t.CODFIL
        AND nfp.CODFOR = t.CODFOR
        AND nfp.NUMNFC = t.NUMNFC
        INNER JOIN SAPIENS_PROD.E420OCP oc ON oc.CODEMP = nfp.CODEMP
        AND oc.CODFIL = nfp.CODFIL
        AND oc.NUMOCP = nfp.NUMOCP
        INNER JOIN SAPIENS_PROD.R999USU uoc ON uoc.CODUSU = oc.USUGER
        INNER JOIN SAPIENS_PROD.E614USU aoc ON aoc.CODEMP = oc.CODEMP
        AND aoc.NUMAPR = oc.NUMAPR
        AND aoc.ROTNAP = oc.ROTNAP
        INNER JOIN SAPIENS_PROD.R999USU uaoc ON uaoc.CODUSU = aoc.USUAPR
    ),
    (
        SAPIENS_PROD.E501MCP m
        LEFT OUTER JOIN SAPIENS_PROD.E066FPG fpm ON fpm.CODEMP = m.CODEMP
        AND fpm.CODFPG = m.CODFPG
        LEFT OUTER JOIN SAPIENS_PROD.E614USU uat ON uat.CODEMP = m.CODEMP
        AND uat.ROTNAP = m.ROTNAP
        AND uat.NUMAPR = m.NUMAPR
    ),
    SAPIENS_PROD.E095FOR fo,
    SAPIENS_PROD.E070FIL fi,
    SAPIENS_PROD.E501RAT rt,
    SAPIENS_PROD.E044CCU crt,
    SAPIENS_PROD.E045PLA pct,
    SAPIENS_PROD.R999USU u,
    SAPIENS_PROD.E001TNS tns
WHERE
    t.CODEMP = m.CODEMP
    AND t.CODEMP = fi.CODEMP
    AND t.CODEMP = pct.codemp
    AND t.CODEMP = rt.CODEMP
    AND rt.CODEMP = crt.CODEMP
    AND rt.CODEMP = pct.CODEMP
    AND m.CODEMP = tns.CODEMP
    AND t.CODFIL = m.CODFIL
    AND t.CODFIL = fi.CODFIL
    AND t.CODFIL = rt.CODFIL
    AND t.NUMTIT = m.NUMTIT
    AND t.NUMTIT = rt.NUMTIT
    AND t.CODTPT = m.CODTPT
    AND t.CODTPT = rt.CODTPT
    AND t.CODFOR = m.CODFOR
    AND t.CODFOR = rt.CODFOR
    AND m.CODEMP = fi.CODEMP
    AND m.CODFIL = fi.CODFIL
    AND fo.CODFOR = t.CODFOR
    AND fo.CODFOR = m.CODFOR
    AND rt.CODCCU = crt.CODCCU
    AND rt.CTARED = pct.CTARED
    AND tt.CODTPT = t.CODTPT
    AND tt.CODTPT = m.CODTPT
    AND m.CODTNS = tns.CODTNS
    AND u.CODUSU = m.USUGER
    AND t.CODEMP = 5
    AND t.USUGER <> 388
    AND t.DATENT = TO_DATE('REPLACE_START_DATE', 'yyyy-mm-dd')
ORDER BY
    t.CODFil