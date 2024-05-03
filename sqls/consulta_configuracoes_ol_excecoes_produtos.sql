SET NOCOUNT ON

SELECT
  configuracao_ol_excecao_prod,
  formulario_origem,
  tab_master_origem,
  reg_master_origem,
  reg_log_inclusao,
  configuracao_ol_excecao,
  produto,
  desconto_para,
  tipo_acao_desconto,
  desconto_para_distribuidora,
  desconto_para_industria,
  contador_f4
FROM
  CONFIGURACOES_OL_EXCECOES_PRODUTOS



