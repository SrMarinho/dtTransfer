SET NOCOUNT ON

SELECT
  A.configuracao_ol_excecao_marca,
  A.formulario_origem,
  A.tab_master_origem,
  A.reg_master_origem,
  A.reg_log_inclusao,
  A.configuracao_ol_excecao,
  A.marca,
  A.desconto_total,
  A.desconto_distribuidora,
  A.desconto_fabricante,
  A.tipo_acao_desconto,
  A.contador_f1,
  A.desconto_de_ini,
  A.desconto_de_fim,
  A.desconto_fabricante_01,
  A.desconto_fabricante_02,
  A.desconto_fabricante_03,
  A.desconto_fabricante_04,
  A.desconto_fabricante_05
FROM
  CONFIGURACOES_OL_EXCECOES_MARCAS A