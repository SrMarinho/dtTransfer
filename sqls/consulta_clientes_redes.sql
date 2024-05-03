SET NOCOUNT ON

SELECT
  cliente_rede,
  formulario_origem,
  tab_master_origem,
  reg_master_origem,
  reg_log_inclusao,
  descricao,
  credito_unificado,
  analisa_credito,
  rede_grupo,
  projeto
FROM
  CLIENTES_REDES


