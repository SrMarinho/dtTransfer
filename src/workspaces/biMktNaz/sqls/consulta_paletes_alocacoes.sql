SELECT PALETE_BARRAS AS palete_barras,
       DATA_HORA AS data_hora,
       CODIGO_LOCALIZADOR AS codigo_localizador,
       ALOCAR_PIKING AS alocar_piking,
       RECEBIMENTO_LANCAMENTO AS recebimento_lancamento,
       CENTRO_ESTOQUE AS centro_estoque,
       PALETE_ALOCACAO_COLETOR AS palete_alocacao_coletor,
       RECEBIMENTO AS recebimento,
       TAREFA AS tarefa,
       QUANTIDADE AS quantidade,
       PRODUTO AS produto,
       LOTE_VALIDADE AS lote_validade,
       CRACHA AS cracha
FROM PALETES_ALOCACOES A
WHERE A.CENTRO_ESTOQUE IN (SELECT A.CENTRO_ESTOQUE FROM OS_EMPRESAS_CENTROS_ESTOQUES_MAPAS A)