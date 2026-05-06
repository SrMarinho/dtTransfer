SELECT
    CODEMP AS empresa_id,
    CODFIL AS filial_id,
    CODSNF AS codigo_serie_nf,
    NUMNFV AS numero_nf,
    DATEMI AS data_emissao,
    TNSPRO AS codigo_transacao_produto,
    TNSSER AS codigo_transacao_servico
FROM SAPIENS_PROD.E140NFV
WHERE DATEMI >= TO_DATE('REPLACE_START_DATE', 'yyyy-mm-dd')
AND DATEMI < TO_DATE('REPLACE_END_DATE', 'yyyy-mm-dd')
