SET NOCOUNT ON

SELECT
  configuracao_ol_excecao_unidade,
  formulario_origem,
  tab_master_origem,
  reg_master_origem,
  reg_log_inclusao,
  configuracao_ol_excecao,
  empresa,
  contador_f2,
  tipo_restricao
FROM
  CONFIGURACOES_OL_EXCECOES_UNIDADES



