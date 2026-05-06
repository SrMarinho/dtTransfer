SELECT
	A.NF_COMPRA_DEVOLUCAO AS nf_compra_devolucao,
	A.DATA_HORA AS data_hora,
	A.NF_COMPRA AS nf_compra,
	A.EMPRESA AS empresa,
	A.NF_NUMERO AS nf_numero,
	A.EMISSAO AS emissao,
	A.MOVIMENTO AS movimento,
	A.SAIDA AS saida
FROM
	NF_COMPRA_DEVOLUCOES A