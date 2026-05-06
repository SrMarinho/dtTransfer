SELECT
	A.CONFIGURACAO_OL	AS apontador,
	A.DESCRICAO			AS descricao,
	A.VALIDADE_INICIAL	AS validade_inicial,
	A.VALIDADE_FINAL	AS validade_final,
	A.TIPO_OL	        AS tipo_apontador,
	A.PROJETO	        AS projeto,
	A.IDENTIFICADOR	    AS identificador,
	A.PROJETO_INDUSTRIA	AS projeto_industria
FROM
	CONFIGURACOES_OL AS A