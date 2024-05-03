SET NOCOUNT ON

SELECT
  configuracao_ol_excecao_des,
  formulario_origem,
  tab_master_origem,
  reg_master_origem,
  reg_log_inclusao,
  configuracao_ol_excecao,
  desconto_de_ini,
  desconto_de_fim,
  desconto_para,
  tipo_acao_desconto,
  desconto_para_distribuidora,
  desconto_para_industria,
  contador_f3
FROM
  CONFIGURACOES_OL_EXCECOES_DESCONTOS



