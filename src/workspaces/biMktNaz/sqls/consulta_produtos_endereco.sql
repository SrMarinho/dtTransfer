SET NOCOUNT ON

DECLARE @CENTRO_ESTOQUE NUMERIC
DECLARE @PRODUTO_INPUT VARCHAR(20)
DECLARE @PRODUTO       NUMERIC                    
DECLARE @EMPRESA       NUMERIC
DECLARE @PRODUTOS_ENDERECO TABLE(
	produto numeric(15,0),
    descricao character varying(255),
    ean character varying(60),
    corredor character varying(10),
    embalagem_industria numeric(6,0),
    fator_embalagem numeric(5,0),
    localizador character varying(60),
    capacidade_cubagem numeric(15,0),
    capacidade_cubagem_minimo numeric(15,0),
    estoque_total numeric(15,4),
    curva character varying(1),
    centro_estoque numeric(15,0)
    
)
                                  
SET @PRODUTO_INPUT = NULL
                                      
SELECT @PRODUTO = dbo.RETORNA_PRODUTO_BARRAS ( @PRODUTO_INPUT, 0, NULL )

DECLARE db_cursor CURSOR FOR 
SELECT EMPRESA
FROM OS_EMPRESAS_CENTROS_ESTOQUES_MAPAS
WHERE EMPRESA <= 19

OPEN db_cursor  
FETCH NEXT FROM db_cursor INTO @EMPRESA

WHILE @@FETCH_STATUS = 0  
BEGIN	
	--PEGA A CENTRO_ESTOQUE--
	SELECT @CENTRO_ESTOQUE = A.CENTRO_ESTOQUE FROM
	OS_EMPRESAS_CENTROS_ESTOQUES_MAPAS A
	WHERE A.EMPRESA = @EMPRESA      

	--PEGA A CURVA DO PRODUTO
	if object_id('tempdb..#TEMP_CURVA') is not null  
	   DROP TABLE #TEMP_CURVA


	SELECT A.PRODUTO,
		   A.CURVA

	  INTO #TEMP_CURVA

	  FROM CURVA_DEMANDA_REDE_ATUAL A WITH(NOLOCK)
	 WHERE A.EMPRESA_COMPRA = @EMPRESA
	   AND ( A.PRODUTO = @PRODUTO OR @PRODUTO IS NULL )

    INSERT INTO @PRODUTOS_ENDERECO                                                             
	SELECT A.PRODUTO AS produto,                         
		   X.DESCRICAO AS descricao,  
		   DBO.CONCATENA_EAN_PRODUTOS(A.PRODUTO) AS ean,
		   D.CORREDOR AS corredor,
		   --Z.CORREDOR AS CORREDOR_PICKING_RESERVA,
		   --I.DESCRICAO AS CLASSIFICACAO_PRODUTO_ESTOQUE_DES,
		   X.EMBALAGEM_INDUSTRIA AS embalagem_industria,
		   X.FATOR_EMBALAGEM AS fator_embalagem,
		   --X.GRUPO_PRODUTO,  
		   --J.DESCRICAO AS GRUPO_PRODUTO_DES,
		   D.DESCRICAO AS localizador,
		   --Z.LOCALIZADOR AS COD_LOCALIZADOR_PICKING_RESERVA,
		   --Z.DESCRICAO AS LOCALIZADOR_PICKING_RESERVA,

		   A.CAPACIDADE_CUBAGEM AS capacidade_cubagem,
		   A.CAPACIDADE_CUBAGEM_MINIMO AS capacidade_cubagem_minimo,
		   --A.CAPACIDADE_CUBAGEM_PICKING_RESERVA,
		   --A.CAPACIDADE_CUBAGEM_MINIMO_PICKING_RESERVA,

		   /*CASE WHEN ISNULL(E.ESTOQUE_SALDO,0) <> 0
				THEN 'S'    
				ELSE 'N'
		   END AS POSSUI_MOVIMENTACAO             ,*/

		   CASE WHEN ISNULL(F.ESTOQUE_SALDO,0) <> 0
				THEN ISNULL(F.ESTOQUE_SALDO,0)
				ELSE 0
		   END AS estoque_total,

		   ISNULL(G.CURVA, 'E') AS curva,
		   @CENTRO_ESTOQUE AS centro_estoque

		   --DBO.CONCATENA_CORREDOR_ESTOQUE_RESERVA ( A.PRODUTO,@CENTRO_ESTOQUE ) AS CORREDORES_RESERVAS
                                                                                       
	  FROM PRODUTOS_LOCAIS                     A WITH(NOLOCK)  
	  JOIN PRODUTOS                            X WITH(NOLOCK) ON X.PRODUTO             = A.PRODUTO                                         
	  JOIN CADASTROS_LOCALIZADORES             D WITH(NOLOCK) ON D.LOCALIZADOR         = A.CODIGO_LOCALIZADOR
	LEFT JOIN CADASTROS_LOCALIZADORES             Z WITH(NOLOCK) ON Z.LOCALIZADOR         = A.CODIGO_LOCALIZADOR_PICKING_RESERVA
	LEFT JOIN ESTOQUE_ATUAL_LOCALIZADORES      E WITH(NOLOCK) ON E.PRODUTO             = A.PRODUTO
															 AND E.CENTRO_ESTOQUE      = A.OBJETO_CONTROLE
															 AND E.CODIGO_LOCALIZADOR  = A.CODIGO_LOCALIZADOR
	LEFT JOIN ESTOQUE_ATUAL_LOCALIZADORES      M WITH(NOLOCK) ON M.PRODUTO             = A.PRODUTO
															 AND M.CENTRO_ESTOQUE      = A.OBJETO_CONTROLE
															 AND M.CODIGO_LOCALIZADOR  = A.CODIGO_LOCALIZADOR_PICKING_RESERVA
                                           
	LEFT JOIN ESTOQUE_ATUAL                    F WITH(NOLOCK) ON F.PRODUTO             = A.PRODUTO
															 AND F.CENTRO_ESTOQUE      = A.OBJETO_CONTROLE
                                           
	LEFT JOIN #TEMP_CURVA                      G WITH(NOLOCK) ON G.PRODUTO             = A.PRODUTO
	LEFT JOIN CLASSIFICACOES_PRODUTOS_ESTOQUE  I WITH(NOLOCK) ON I.CLASSIFICACAO_PRODUTO_ESTOQUE = X.CLASSIFICACAO_PRODUTO_ESTOQUE
	LEFT JOIN GRUPOS_PRODUTOS                  J WITH(NOLOCK) ON J.GRUPO_PRODUTO       = X.GRUPO_PRODUTO

                                               
	 WHERE A.OBJETO_CONTROLE = @CENTRO_ESTOQUE
	   AND ( X.PRODUTO = @PRODUTO OR @PRODUTO IS NULL )

	ORDER BY A.PRODUTO;

	FETCH NEXT FROM db_cursor INTO @EMPRESA
END 

CLOSE db_cursor  
DEALLOCATE db_cursor

SELECT * FROM @PRODUTOS_ENDERECO