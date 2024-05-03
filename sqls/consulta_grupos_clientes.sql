SET NOCOUNT ON

SELECT
  grupo_cliente,
  formulario_origem,
  tab_master_origem,
  reg_master_origem,
  reg_log_inclusao,
  descricao
FROM
  GRUPOS_CLIENTES

