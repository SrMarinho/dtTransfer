SET NOCOUNT OFF

SELECT
  configuracao_ol_excecao_cliente,
  formulario_origem,
  tab_master_origem,
  reg_master_origem,
  reg_log_inclusao,
  configuracao_ol_excecao,
  entidade,
  cliente_rede,
  grupo_cliente,
  contador_f6,
  tipo_restricao
FROM
  CONFIGURACOES_OL_EXCECOES_CLIENTES


