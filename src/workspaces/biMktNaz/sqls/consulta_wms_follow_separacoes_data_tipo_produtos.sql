 SET NOCOUNT ON

 -------   Gera Tabela Temporária das Empresas do Usuário Logado   -------
if object_id('tempdb..#TEMP_EMPRESAS_USER') is not null
   DROP TABLE #TEMP_EMPRESAS_USER
   
SELECT * INTO #TEMP_EMPRESAS_USER  FROM UDF_USUARIO_EMPRESAS('')   

if object_id('#temp_wms_follow_separacao_data_tipo_produtos') is not null
   DROP TABLE #temp_wms_follow_separacao_data_tipo_produtos

DECLARE @RESULTADO TABLE (
    pedido_venda NUMERIC(15, 0),
    data DATETIME,
    tipo_romaneio VARCHAR(60),
    produto NUMERIC(15, 0),
    descricao VARCHAR(255),
    empresa_origem NUMERIC(15, 0),
    centro_estoque_origem NUMERIC(15, 0),
    entidade_destino NUMERIC(15, 0),
    nome_entidade_destino VARCHAR(60),
    rota NUMERIC(15, 0),
    rota_descricao VARCHAR(60),
    qtde_original NUMERIC(38, 2),
    qtde_separacao NUMERIC(38, 2),
    qtde_conferencia NUMERIC(38, 2),
    saldo NUMERIC(38, 2),
    qtde_n_atendida NUMERIC(38, 2),
    notas VARCHAR(1000),
    CHECKOUTS NUMERIC(15, 0)
);

  -------------------------------------------------------------------------
                       
-- DECLARE @DATA_INI               VARCHAR(32)
-- DECLARE @DATA_FIM               VARCHAR(32)
DECLARE @ENTIDADE_DESTINO       NUMERIC                                   
DECLARE @PRODUTO_FILTRO         NUMERIC
DECLARE @ABRIR_SEPARADOR        VARCHAR(1)
DECLARE @APENAS_COM_SALDO       VARCHAR(1)
DECLARE @GRUPO_CLIENTE          NUMERIC(15)
DECLARE @TIPO_FILTRO            VARCHAR(1) = 'T'

DECLARE @EMPRESA                NUMERIC(15);
DECLARE @CENTRO_ESTOQUE NVARCHAR(50);

DECLARE cursor_empresas CURSOR FOR
SELECT EMPRESA, CENTRO_ESTOQUE
FROM OS_EMPRESAS_CENTROS_ESTOQUES_MAPAS WHERE EMPRESA <= 19;


OPEN cursor_empresas;

FETCH NEXT FROM cursor_empresas INTO @EMPRESA, @CENTRO_ESTOQUE;

--SET @EMPRESA = 'REPLACE_EMPRESA_HERE'
--SET @CENTRO_ESTOQUE_ORIGEM = (SELECT A.CENTRO_ESTOQUE FROM OS_EMPRESAS_CENTROS_ESTOQUES_MAPAS A WHERE A.EMPRESA  = @EMPRESA)
                   
    --SET @CENTRO_ESTOQUE_ORIGEM = 1000          
    --SET @DATA_INI = '09/02/2015'                    
    --SET @DATA_FIM = '09/02/2015'                                               
    --SET @ABRIR_SEPARADOR  ='S'                                            
    --SET @APENAS_COM_SALDO = 'S'

    --SET @CENTRO_ESTOQUE_ORIGEM =:CENTRO_ESTOQUE_ORIGEM
    --SET @DATA_INI = CAST('2024-09-02' AS DATE)
    -- SET @DATA_FIM = CAST('2024-07-05' AS DATETIME)
    SET @ABRIR_SEPARADOR ='N'      
    SET @APENAS_COM_SALDO ='T'
                         

IF @TIPO_FILTRO IS NULL OR @TIPO_FILTRO = '' SET @TIPO_FILTRO = 'T'
IF @APENAS_COM_SALDO IS NULL OR @APENAS_COM_SALDO = '' SET @APENAS_COM_SALDO = 'T'

WHILE @@FETCH_STATUS = 0
BEGIN
--TRANSFERENCIAS GERADAS--

--TRANSFERENCIAS GERADAS--
if object_id('tempdb..#SEL_ESTOQUE_TRANSFERENCIAS') is not null
   DROP TABLE #SEL_ESTOQUE_TRANSFERENCIAS;

SELECT A.ESTOQUE_TRANSFERENCIA             AS ESTOQUE_TRANSFERENCIA,
       A.MAPA                              AS MAPA,
       ISNULL(C.PLANEJADO, 'N')            AS PLANEJADO,
       A.PEDIDO_VENDA                      AS PEDIDO_VENDA,
       ISNULL(D.DESCRICAO, 'Pedido Venda') AS TIPO,
       A.CENTRO_ESTOQUE_DESTINO            AS CENTRO_ESTOQUE_DESTINO,
       A.CENTRO_ESTOQUE_ORIGEM             AS CENTRO_ESTOQUE_ORIGEM,
       A.EMPRESA                           AS EMPRESA_ORIGEM,
       X.ROTA                              AS ROTA,
       ISNULL(A.ENTIDADE, E.ENTIDADE)      AS ENTIDADE_DESTINO,
       A.MOVIMENTO                         AS MOVIMENTO,
       A.SEPARADOR_ROMANEIO                AS SEPARADOR,
       A.TIPO_ESTOQUE                      AS TIPO_ESTOQUE,
       G.DESCRICAO                         AS TIPO_ESTOQUE_DESCRICAO

  INTO #SEL_ESTOQUE_TRANSFERENCIAS

  FROM ESTOQUE_TRANSFERENCIAS                     A WITH(NOLOCK)
  JOIN #TEMP_EMPRESAS_USER                        Y WITH(NOLOCK) ON Y.EMPRESA_USUARIA              = A.EMPRESA
  LEFT JOIN MAPA_TRANSFERENCIAS                   C WITH(NOLOCK) ON C.MAPA                         = A.MAPA
  LEFT JOIN TIPOS_MAPA_TRANSFERENCIA              D WITH(NOLOCK) ON D.TIPO_MAPA                    = C.TIPO_MAPA
  LEFT JOIN EMPRESAS_ESTOQUE_PADRAO               E WITH(NOLOCK) ON E.CENTRO_ESTOQUE               = A.CENTRO_ESTOQUE_DESTINO
  LEFT JOIN TIPOS_ESTOQUE_TRANSFERENCIAS          G WITH(NOLOCK) ON G.TIPO_ESTOQUE                 = A.TIPO_ESTOQUE
  OUTER APPLY DBO.ENTIDADES_ROTAS_DATA ( A.ENTIDADE, A.MOVIMENTO) X
 WHERE CAST(A.MOVIMENTO AS DATE) >= DATEADD(DAY, -1, CAST(GETDATE() AS DATE))
    AND CAST(A.MOVIMENTO AS DATE) <= CAST(GETDATE() AS DATE)
   AND ( A.CENTRO_ESTOQUE_ORIGEM        = @CENTRO_ESTOQUE OR @CENTRO_ESTOQUE IS NULL )
   AND ( A.EMPRESA                      = @EMPRESA               OR @EMPRESA               IS NULL )
   AND ( ( @TIPO_FILTRO  ='R' AND A.RESSUPRIMENTO = 'S' ) OR
         ( @TIPO_FILTRO  ='V' AND A.PEDIDO_VENDA   > 0 ) OR
         ( @TIPO_FILTRO  ='T' ) )
   AND X.EMPRESA = A.EMPRESA
OPTION(MAXDOP 0, RECOMPILE);

ALTER TABLE #SEL_ESTOQUE_TRANSFERENCIAS ADD PRIMARY KEY CLUSTERED(ESTOQUE_TRANSFERENCIA)

--------------------------------------------------------
-- atualiza o separador
--------------------------------------------------------
UPDATE A
   SET SEPARADOR = CASE WHEN @ABRIR_SEPARADOR = 'S'
                        THEN ISNULL(F.SEPARADOR,A.SEPARADOR)
                        ELSE NULL
                   END 
  FROM #SEL_ESTOQUE_TRANSFERENCIAS        A
  JOIN ESTOQUE_TRANSFERENCIAS_SEPARADORES F WITH(NOLOCK) ON F.ESTOQUE_TRANSFERENCIA = A.ESTOQUE_TRANSFERENCIA;


if object_id('tempdb..#TRASNFERENCIAS_GERADAS') is not null
   DROP TABLE #TRASNFERENCIAS_GERADAS;
     
SELECT A.ESTOQUE_TRANSFERENCIA         AS ESTOQUE_TRANSFERENCIA,
       A.MAPA                          AS MAPA,
       A.PLANEJADO                     AS PLANEJADO,
       A.PEDIDO_VENDA                  AS PEDIDO_VENDA,
       B.PRODUTO                       AS PRODUTO,
       A.TIPO                          AS TIPO,
       A.CENTRO_ESTOQUE_DESTINO        AS CENTRO_ESTOQUE_DESTINO,
       A.CENTRO_ESTOQUE_ORIGEM         AS CENTRO_ESTOQUE_ORIGEM,
       A.EMPRESA_ORIGEM                AS EMPRESA_ORIGEM,
       A.ROTA                          AS ROTA,
       A.ENTIDADE_DESTINO              AS ENTIDADE_DESTINO,
       A.MOVIMENTO                     AS DATA,
       SUM(B.QTDE_ORIGINAL)            AS QTDE_ORIGINAL,
       SUM(B.SEPARACAO)                AS SEPARACAO,
       SUM(B.CONFERENCIA)              AS CONFERENCIA,
       SUM(B.SALDO)                    AS SALDO,
       A.SEPARADOR                     AS SEPARADOR,
       A.TIPO_ESTOQUE,
       A.TIPO_ESTOQUE_DESCRICAO
              
     INTO #TRASNFERENCIAS_GERADAS

     FROM #SEL_ESTOQUE_TRANSFERENCIAS                A WITH(NOLOCK)
     JOIN ESTOQUE_TRANSFERENCIAS_SALDO               B WITH(NOLOCK) ON B.ESTOQUE_TRANSFERENCIA        = A.ESTOQUE_TRANSFERENCIA 
 WHERE ( B.PRODUTO = @PRODUTO_FILTRO OR @PRODUTO_FILTRO IS NULL )
   AND ( ( @APENAS_COM_SALDO = 'S' AND (B.SALDO) > 0 ) OR
         ( @APENAS_COM_SALDO = 'N' AND (B.SALDO)<= 0 ) OR
         ( @APENAS_COM_SALDO = 'T' ) )

GROUP BY A.ESTOQUE_TRANSFERENCIA  ,
         A.MAPA                   ,
         A.PEDIDO_VENDA           ,
         A.CENTRO_ESTOQUE_DESTINO ,
         A.CENTRO_ESTOQUE_ORIGEM  ,
         A.EMPRESA_ORIGEM         ,
         A.ROTA                   ,
         A.MOVIMENTO              ,
         A.ENTIDADE_DESTINO       ,
         A.TIPO                   ,
         A.PLANEJADO              ,
         B.PRODUTO                ,
         A.SEPARADOR              ,
         A.TIPO_ESTOQUE           ,
         A.TIPO_ESTOQUE_DESCRICAO

   CREATE NONCLUSTERED INDEX [IX_#TRASNFERENCIAS_GERADAS_001] ON [dbo].[#TRASNFERENCIAS_GERADAS] ([ESTOQUE_TRANSFERENCIA],[PRODUTO])

   if object_id('tempdb..#TRASNFERENCIAS_NOTAS') is not null
      DROP TABLE #TRASNFERENCIAS_NOTAS

   SELECT C.ESTOQUE_TRANSFERENCIA,
          B.PRODUTO,
          DBO.CONCATENA_NOTAS_TRANSFERENCIAS_PRODUTO ( C.ESTOQUE_TRANSFERENCIA, B.PRODUTO ) AS NOTAS,
          SUM(B.QUANTIDADE_ESTOQUE) AS QUANTIDADE_NOTA

    INTO #TRASNFERENCIAS_NOTAS         

     FROM NF_FATURAMENTO                        A WITH(NOLOCK)
     JOIN #TEMP_EMPRESAS_USER                   Y WITH(NOLOCK) ON Y.EMPRESA_USUARIA       = A.EMPRESA
     JOIN NF_FATURAMENTO_PRODUTOS_LOTE_VALIDADE B WITH(NOLOCK) ON B.NF_FATURAMENTO        = A.NF_FATURAMENTO
     JOIN #TRASNFERENCIAS_GERADAS               C WITH(NOLOCK) ON C.ESTOQUE_TRANSFERENCIA = B.ESTOQUE_TRANSFERENCIA
                                                              AND C.PRODUTO               = B.PRODUTO
LEFT JOIN CANCELAMENTOS_NOTAS_FISCAIS           D WITH(NOLOCK) ON D.CHAVE                 = A.NF_FATURAMENTO
                                                              AND D.TIPO                  = 1

    WHERE D.NF_CANCELAMENTO IS NULL


     GROUP BY C.ESTOQUE_TRANSFERENCIA,
              B.PRODUTO,
              DBO.CONCATENA_NOTAS_TRANSFERENCIAS ( C.ESTOQUE_TRANSFERENCIA );

INSERT INTO @RESULTADO
   
SELECT --A.ESTOQUE_TRANSFERENCIA,
       --A.MAPA,
       --A.PLANEJADO,
       A.PEDIDO_VENDA AS pedido_venda,
       A.DATA AS data,
       --A.TIPO,
       A.TIPO_ESTOQUE_DESCRICAO as tipo_romaneio,
       A.PRODUTO AS produto,
       C.DESCRICAO AS descricao,
       --A.SEPARADOR,
       --D.NOME,
       A.EMPRESA_ORIGEM AS empresa_origem,
       A.CENTRO_ESTOQUE_ORIGEM AS centro_estoque_origem,
       A.ENTIDADE_DESTINO AS entidade_destino,
       B.NOME   AS nome_entidade_destino,

       A.ROTA as rota,
       Y.DESCRICAO AS rota_descricao,

       SUM(A.QTDE_ORIGINAL)     AS qtde_original,
       SUM(A.SEPARACAO)         AS qtde_separacao,
       SUM(A.CONFERENCIA)       AS qtde_conferencia,
       SUM(A.SALDO)             AS saldo,
       --SUM(ISNULL(E.QUANTIDADE_NOTA,0))   AS QUANTIDADE_NOTA,
       SUM(A.QTDE_ORIGINAL) -
       SUM(A.CONFERENCIA)   AS qtde_n_atendida,
       
      --( SUM(A.CONFERENCIA) / SUM(A.QTDE_ORIGINAL) ) * 100
      --                          AS PERC_ATENDIDO,
                                
     --( ( SUM(A.QTDE_ORIGINAL) - SUM(A.CONFERENCIA) )  / SUM(A.QTDE_ORIGINAL) ) * 100
       --                         AS PERC_N_ATENDIDO,

       E.NOTAS AS notas,
       --DBO.CONCATENA_PALETES_TRANSFERENCIAS   ( A.ESTOQUE_TRANSFERENCIA ) AS PALETES,
       A.ESTOQUE_TRANSFERENCIA AS CHECKOUTS
  FROM #TRASNFERENCIAS_GERADAS                   A
  JOIN ENTIDADES                                 B ON B.ENTIDADE              = A.ENTIDADE_DESTINO
  JOIN PRODUTOS                                  C ON C.PRODUTO               = A.PRODUTO
  LEFT JOIN ENTIDADES                            D ON D.ENTIDADE              = A.SEPARADOR
  LEFT JOIN #TRASNFERENCIAS_NOTAS                E ON E.ESTOQUE_TRANSFERENCIA = A.ESTOQUE_TRANSFERENCIA
                                                               AND E.PRODUTO               = A.PRODUTO
  LEFT JOIN PEDIDOS_VENDAS_PARAMETROS_ENTIDADES  F ON F.ENTIDADE              = B.ENTIDADE
  LEFT JOIN ROTAS_FATURAMENTOS                   Y ON Y.ROTA                  = A.ROTA
 WHERE 1=1
   AND ( F.GRUPO_CLIENTE = @GRUPO_CLIENTE OR @GRUPO_CLIENTE IS NULL )
  
  GROUP BY A.TIPO,
           A.CENTRO_ESTOQUE_ORIGEM,
           A.EMPRESA_ORIGEM,
           A.DATA,
           A.ENTIDADE_DESTINO,
           B.NOME,
           A.ROTA,
           Y.DESCRICAO,
           A.ESTOQUE_TRANSFERENCIA,
           A.MAPA,
           A.PLANEJADO,
           A.PEDIDO_VENDA,
           A.SEPARADOR,
           D.NOME,
           E.NOTAS,                          
           DBO.CONCATENA_PALETES_TRANSFERENCIAS  ( A.ESTOQUE_TRANSFERENCIA ),
           DBO.CONCATENA_CHECKOUT_TRANSFERENCIAS_PRODUTO ( A.ESTOQUE_TRANSFERENCIA, A.PRODUTO ),
           A.PRODUTO,
           C.DESCRICAO,
           A.TIPO_ESTOQUE_DESCRICAO               
                         
  HAVING SUM(A.QTDE_ORIGINAL) > 0 

  ORDER BY DATA, DESCRICAO;

  FETCH NEXT FROM cursor_empresas INTO @EMPRESA, @CENTRO_ESTOQUE;
  END

CLOSE cursor_empresas;
DEALLOCATE cursor_empresas;

select 
	A.*,
	C.DESCRICAO AS status_pedidos_vendas
from 
	@RESULTADO A
	LEFT join PEDIDOS_VENDAS_STATUS B WITH(NOLOCK) ON B.PEDIDO_VENDA = A.PEDIDO_VENDA
	LEFT JOIN STATUS_PEDIDOS_VENDAS C WITH(NOLOCK) ON C.STATUS_PEDIDO_VENDA = B.STATUS_PEDIDO_VENDA
OPTION(MAXDOP 0, RECOMPILE)