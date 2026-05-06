SELECT A.EMPRESA AS unidade,
       A.NF_NUMERO AS nota_fiscal,
       CAST(A.EMISSAO_NFE as datetime) AS data_emissao,
       '1' AS tipo_nota,
       ISNULL (A.VENDEDOR, A.DONO) AS vendedor,
       ISNULL (A.DONO, A.VENDEDOR) AS setor,
       A.ENTIDADE AS codigo_cliente,
       B.DATA_HORA AS data_pedido,
       B.PEDIDO_VENDA AS pedido_venda,
       C.ORIGEM_VENDA_CANAL AS origem_venda_canal,
       C.DESCRICAO AS origem_venda_canal_descricao,
       B.CONFIGURACAO_OL AS apontador,
       F.STATUS AS status_nota,
       MAX(D.DATA_HORA) AS dt_liberacao
    FROM NF_FATURAMENTO            A WITH (NOLOCK)
    JOIN OPERACOES_FISCAIS         E WITH (NOLOCK) ON E.OPERACAO_FISCAL    = A.OPERACAO_FISCAL
    JOIN PEDIDOS_VENDAS            B WITH (NOLOCK) ON B.PEDIDO_VENDA       = A.PEDIDO_VENDA
    JOIN ORIGENS_VENDAS_CANAIS     C WITH (NOLOCK) ON C.ORIGEM_VENDA_CANAL = B.ORIGEM_VENDA_CANAL
    JOIN NFE_CABECALHO             F WITH (NOLOCK) ON F.FORMULARIO_ORIGEM  = A.FORMULARIO_ORIGEM
                                                  AND F.TAB_MASTER_ORIGEM  = A.TAB_MASTER_ORIGEM
                                                  AND F.REG_MASTER_ORIGEM  = A.NF_FATURAMENTO
    JOIN SOLICITACOES_FATURAMENTOS D WITH (NOLOCK) ON D.PEDIDO_VENDA       = A.PEDIDO_VENDA
        WHERE E.TIPO_OPERACAO IN (3, 10)
        AND CAST(A.EMISSAO AS DATE) = 'REPLACE_START_DATE'
GROUP BY A.EMPRESA,
            A.NF_NUMERO,
            CAST(A.EMISSAO_NFE as datetime),
            A.VENDEDOR,
            A.DONO,
            A.ENTIDADE,
            B.DATA_HORA,
            B.PEDIDO_VENDA,
            C.ORIGEM_VENDA_CANAL,
            C.DESCRICAO,
            B.CONFIGURACAO_OL,
            F.STATUS

UNION

SELECT DISTINCT
    A.EMPRESA AS unidade,
    ISNULL (A.NF_NUMERO_CLIENTE, A.NF_NUMERO) AS nota_fiscal,
    CAST(B.MOVIMENTO as datetime) AS data_emissao,
    '2' AS tipo_nota,
    ISNULL (A.VENDEDOR, C.VENDEDOR) AS vendedor,
    C.VENDEDOR AS setor,
    A.ENTIDADE AS codigo_cliente,
    NULL AS data_pedido,
    NULL AS pedido_venda,
    NULL AS origem_venda_canal,
    NULL AS origem_venda_canal_descricao,
    NULL AS apontador,
    NULL AS status_nota,
    NULL AS dt_liberacao
FROM
    NF_FATURAMENTO_DEVOLUCOES A
WITH
    (NOLOCK)
    JOIN VENDAS_ANALITICAS B
WITH
    (NOLOCK) ON B.FORMULARIO_ORIGEM = A.FORMULARIO_ORIGEM
    AND B.TAB_MASTER_ORIGEM = A.TAB_MASTER_ORIGEM
    AND B.REG_MASTER_ORIGEM = A.NF_FATURAMENTO_DEVOLUCAO
    JOIN ENTIDADES_DONOS_EMPRESAS C
WITH
    (NOLOCK) ON C.ENTIDADE = A.ENTIDADE
    AND C.EMPRESA = A.EMPRESA
WHERE
    CAST(B.MOVIMENTO AS DATE) = 'REPLACE_START_DATE'


