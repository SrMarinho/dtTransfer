SELECT
    CODEMP AS empresa_id,
    CODFIL AS filial_id,
    CODFOR AS fornecedor_id,
    NUMNFC AS numero_nf,
    CODSNF AS codigo_serie_nf,
    DATENT AS data_entrada,
    TNSPRO AS codigo_transacao_produto,
    TNSSER AS codigo_transacao_servico
FROM SAPIENS_PROD.E440NFC
WHERE DATENT >= TO_DATE('REPLACE_START_DATE', 'yyyy-mm-dd')
AND DATENT < TO_DATE('REPLACE_END_DATE', 'yyyy-mm-dd')
