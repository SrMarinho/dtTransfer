SELECT
[Cod. Campanha] AS id_campanha,
[Sub Campanha_temp] AS subcampanha,
[Cod. Universo] AS codigo_universo,
T928_DESCRICAO AS descricao,
T928_OBS AS observacao,
[Bloqueio/Restrito] AS tipo_restricao,
Tipo AS tipo
FROM VW_PARTICIPANTES_CAMPANHAS;