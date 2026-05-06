SELECT
    CODEMP AS empresa_id,
    CODTNS AS codigo_transacao,
    LISMOD AS modulo,
    DESTNS AS descricao_transacao,
    COMNOP AS cfop_codigo,
    ACEMAN AS tipo_operacao
FROM SAPIENS_PROD.E001TNS
