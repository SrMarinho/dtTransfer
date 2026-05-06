SELECT
	A.RESTRICAO_PEDIDO_VENDA_CLIENTE AS restricao_pedido_venda_cliente,
	A.RESTRICAO_PEDIDO_VENDA		 AS restricao_pedido_venda,
	A.CODIGO_CLIENTE				 AS codigo_cliente,
	A.CODIGO_GRUPO					 AS codigo_grupo,
	A.CODIGO_REDE					 AS codigo_rede,
	A.TIPO_RESTRICAO				 AS tipo_restricao,
	A.DESCRICAO						 AS descricao,
	A.EMPRESA						 AS empresa
FROM
	RESTRICOES_PEDIDOS_VENDAS_CLIENTES A