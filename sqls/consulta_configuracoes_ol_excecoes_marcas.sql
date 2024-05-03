SET NOCOUNT ON

SELECT
  configuracao_ol_excecao_marca,
  formulario_origem,
  tab_master_origem,
  reg_master_origem,
  reg_log_inclusao,
  configuracao_ol_excecao,
  marca,
  desconto_total,
  desconto_distribuidora,
  desconto_fabricante,
  tipo_acao_desconto,
  contador_f1,
  desconto_de_ini,
  desconto_de_fim
FROM
  CONFIGURACOES_OL_EXCECOES_MARCAS


