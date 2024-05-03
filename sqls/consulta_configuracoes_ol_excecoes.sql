SET NOCOUNT ON

SELECT
  configuracao_ol_excecao,
  formulario_origem,
  tab_master_origem,
  reg_master_origem,
  reg_log_inclusao,
  usuario_logado,
  data_hora,
  descricao,
  validade_inicial,
  validade_final,
  entidade,
  cliente_rede,
  grupo_cliente,
  tipo_origem_desconto,
  identificador
FROM
  CONFIGURACOES_OL_EXCECOES




