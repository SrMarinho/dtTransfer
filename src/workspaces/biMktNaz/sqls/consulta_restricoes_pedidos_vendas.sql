SELECT
	A.RESTRICAO_PEDIDO_VENDA AS restricao_pedido_venda,
	A.DATA_HORA AS data_hora,
	A.DESCRICAO AS descricao,
	A.PEDIDO_VENDA_PARAMETRO_ENTIDADE AS pedido_venda_parametro_entidade,
	A.OBSERVACAO AS observacao,
	A.MOVIMENTO_INICIAL AS movimento_inicial,
	A.MOVIMENTO_FINAL AS movimento_final
FROM 
	RESTRICOES_PEDIDOS_VENDAS A