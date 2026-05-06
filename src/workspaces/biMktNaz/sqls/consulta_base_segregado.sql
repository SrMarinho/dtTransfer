SET NOCOUNT ON
IF OBJECT_ID('TEMPDB..#TEMP_PRODUTOS') IS NOT NULL DROP TABLE #TEMP_PRODUTOS
SELECT A.PRODUTO                              AS produto,
       D.DESCRICAO                            AS produto_descricao,
       E.MARCA                                AS marca,
       E.DESCRICAO                            AS marca_descricao,
       A.CENTRO_ESTOQUE                       AS centro_estoque,
       B.DESCRICAO                            AS centro_estoque_descricao,
       B.EMPRESA                              AS empresa,
       A.LOTE                                 AS lote,
       CAST(A.VALIDADE AS DATE)               AS validade,
       CAST(SUM(A.ESTOQUE_SALDO) AS INTEGER)  AS estoque_saldo,
       A.CODIGO_LOCALIZADOR                   AS codigo_localizador,
       C.DESCRICAO                            AS codigo_localizador_descricao,
       'E'                                    AS curva,
       IIF(D.SITUACAO_PRODUTO = 1, 'A', 'I')  AS situacao_produto,
       CAST(N'SEM COMPRADOR' AS VARCHAR(255)) AS comprador
    INTO #TEMP_PRODUTOS
    FROM ESTOQUE_ATUAL_LOCALIZADORES_LV A WITH(NOLOCK)
    JOIN CENTROS_ESTOQUE                B WITH(NOLOCK) ON B.OBJETO_CONTROLE = A.CENTRO_ESTOQUE
    JOIN CADASTROS_LOCALIZADORES        C WITH(NOLOCK) ON C.LOCALIZADOR     = A.CODIGO_LOCALIZADOR
    JOIN PRODUTOS                       D WITH(NOLOCK) ON D.PRODUTO         = A.PRODUTO
    JOIN MARCAS                         E WITH(NOLOCK) ON E.MARCA           = D.MARCA
        WHERE B.TIPO_ESTOQUE = 5
        GROUP BY A.PRODUTO, A.CENTRO_ESTOQUE, B.DESCRICAO, A.LOTE, A.VALIDADE, B.EMPRESA, A.CODIGO_LOCALIZADOR, C.DESCRICAO, D.DESCRICAO, E.MARCA, E.DESCRICAO, D.SITUACAO_PRODUTO
        HAVING SUM(ESTOQUE_SALDO) <> 0

UPDATE A SET A.CURVA = B.CURVA
    FROM #TEMP_PRODUTOS A WITH(NOLOCK)
    JOIN VALOR_BASE     B WITH(NOLOCK) ON B.PRODUTO = A.PRODUTO
                                      AND B.EMPRESA = A.EMPRESA
                                      AND B.ANO     = YEAR(GETDATE())
                                      AND B.MES     = MONTH(GETDATE())

UPDATE A SET A.comprador = C.NOME
    FROM #TEMP_PRODUTOS       A WITH(NOLOCK)
    JOIN PRODUTOS_COMPRADORES B WITH(NOLOCK) ON B.PRODUTO   = A.produto
    JOIN COMPRADORES          C WITH(NOLOCK) ON C.COMPRADOR = B.COMPRADOR



DECLARE @start_date VARCHAR(32) = 'REPLACE_START_DATE'
DECLARE @end_date VARCHAR(32) = 'REPLACE_END_DATE'

SELECT
	A.*,
	B.CUSTO_GERENCIAL AS custo_gerencial,
	B.CUSTO_CONTABIL AS custo_contabil
FROM #TEMP_PRODUTOS A
LEFT JOIN CUSTO_MEDIO_MENSAL_EMPRESA_CONTABIL B ON B.PRODUTO = A.produto AND B.EMPRESA_CONTABIL = A.empresa
WHERE B.ANO BETWEEN YEAR(@start_date) AND YEAR(@end_date) AND B.MES BETWEEN MONTH(@start_date) AND MONTH(@end_date);
