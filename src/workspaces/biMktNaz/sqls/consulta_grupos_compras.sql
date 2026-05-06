SELECT
  A.grupo_compra,
  A.descricao,
  B.EMPRESA,
  A.data_hora,
  A.usuario_logado,
  A.obrigatorio_aprovacao,
  A.dias_curva_a,
  A.dias_curva_b,
  A.dias_curva_c,
  B.leadtime,
  A.comprador,
  A.dias_curva_d,
  A.dias_curva_e,
  A.fornecedor,
  A.leadtime_teorico,
  A.dias_emissao,
  A.data_hora_atualizacao_lt,
  A.vincular_comprador,
  B.LEADTIME_ACORDADO,
  C.MARCA
FROM
	GRUPOS_COMPRAS A
	LEFT JOIN GRUPOS_COMPRAS_EMPRESAS B ON B.GRUPO_COMPRA = A.GRUPO_COMPRA
	LEFT JOIN GRUPOS_COMPRAS_MARCAS C ON C.GRUPO_COMPRA = A.GRUPO_COMPRA