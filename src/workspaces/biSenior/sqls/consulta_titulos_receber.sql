SELECT
    CODEMP AS empresa_id,
    CODFIL AS filial_id,
    CODTPT AS tipo_titulo_id,
    NUMTIT AS numero_titulo,
    CODTNS AS codigo_transacao,
    CODSNF AS codigo_serie_nf,
    NUMNFV AS numero_nf,
    DATEMI AS data_emissao,
    VCTORI AS data_vencimento_original,
    DATPPT AS data_pagamento_previsto,
    ULTPGT AS data_ultimo_pagamento,
    CODPOR AS portador_id,
    CODCRT AS carteira_id,
    CODCLI AS cliente_id,
    CODREP AS representante_id,
    NUMCTR AS numero_contrato,
    SITTIT AS status_titulo,
    VLRORI AS valor_original,
    VLRABE AS valor_aberto,
    PERMUL AS percentual_multa,
    PERJRS AS percentual_juros,
    TIPJRS AS tipo_juros,
    VLRDSC AS valor_desconto
FROM SAPIENS_PROD.E301TCR
WHERE VCTORI >= TO_DATE('REPLACE_START_DATE', 'yyyy-mm-dd')
AND VCTORI < TO_DATE('REPLACE_END_DATE', 'yyyy-mm-dd')
