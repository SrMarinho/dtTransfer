SELECT
	A.RESTRICAO_PEDIDO_VENDA_UF AS restricao_pedido_venda_uf,
	A.RESTRICAO_PEDIDO_VENDA	AS restricao_pedido_venda,
	A.UF						AS uf,
	A.TIPO_RESTRICAO			AS tipo_restricao,
	A.EMPRESA					AS empresa
FROM
	RESTRICOES_PEDIDOS_VENDAS_UF A