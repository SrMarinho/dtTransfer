SELECT
	A.NF_COMPRA_DEVOLUCAO AS nf_compra_devolucoes,
	A.PEDIDO_COMPRA AS pedido_compra,
	A.PEDIDO_COMPRA_PRODUTO AS pedido_compra_produto,
	A.REFERENCIA AS referencia,
	A.PRODUTO AS produto,
	A.QUANTIDADE AS quantidade,
	A.UNIDADE_MEDIDA AS unidade_medida,
	A.VALOR_UNITARIO AS valor_unitario,
	A.DESCONTO AS desconto,
	A.TOTAL_DESCONTO AS total_desconto,
	A.TOTAL_PRODUTO AS total_produto,
	A.LOTE AS lote,
	A.VALIDADE AS validade,
	A.NF_COMPRA_PRODUTO AS nf_compra_produto
FROM
	NF_COMPRA_DEVOLUCOES_PRODUTOS AS A