SET NOCOUNT ON

SELECT
  configuracao_ol_excecao_ol,
  formulario_origem,
  tab_master_origem,
  reg_master_origem,
  reg_log_inclusao,
  configuracao_ol_excecao,
  configuracao_ol,
  tipo_acao_desconto,
  contador_f5
FROM
  CONFIGURACOES_OL_EXCECOES_OLS

