SELECT [Cod. Campanha],
       CAST([Data Inicial] AS DATE) AS [Data Inicial],
       CAST([Data Final] AS DATE) AS [Data Final],
       Campanha,
       [Email Envio Campanha],
       [Enviar Totais CD],
       T926_SITUACAO,
       T926_TIPO_OBJETIVO,
       T926_TIPO_PARTICIPANTE,
       CONCAT(C.USUARIO_LOGADO, ' - ', D.NOME) AS criado_por
    FROM VW_CAMPANHAS B
    JOIN CONFIGURACOES_CAMPANHAS C ON C.CONFIGURACAO_CAMPANHA = B.[Cod. Campanha]
    JOIN USUARIOS                D ON D.USUARIO               = C.USUARIO_LOGADO