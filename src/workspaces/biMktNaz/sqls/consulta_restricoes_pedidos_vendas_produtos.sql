SELECT
	A.RESTRICAO_PEDIDO_VENDA_PRODUTO	AS restricao_pedido_venda_produto,
	A.RESTRICAO_PEDIDO_VENDA			AS restricao_pedido_venda,
	A.PRODUTO							AS produto,
	A.TIPO_RESTRICAO					AS tipo_restricao
FROM
	RESTRICOES_PEDIDOS_VENDAS_PRODUTOS A