SELECT A.PRODUTO                AS codigo_produto,
       ISNULL(B.EAN, A.PRODUTO) AS ean,
       NULL                     AS dum,
       A.DESCRICAO              AS descricao,
       C.DESCRICAO              AS familia,
       (SELECT TOP 1 Z.DESCRICAO
        FROM PRODUTOS_DCB     X WITH(NOLOCK)
        JOIN DCB_MEDICAMENTOS Z WITH(NOLOCK) ON Z.DCB = X.DCB
        WHERE X.PRODUTO = A.PRODUTO)         AS molecula,
       NULL                                  AS franquia,
       E.DESCRICAO                           AS categoria,
       NULL                                  AS classificacao,
       IIF(A.SITUACAO_PRODUTO = 1, 'A', 'I') AS situacao,
       NULL                                  AS curva,
       NULL                                  AS legenda,
       A.EMBALAGEM_INDUSTRIA                 AS embalagem,
       ISNULL(A.MARCA, 0)                    AS laboratorio_id,
       D.DESCRICAO                           AS grupo_produto,
       G.DESCRICAO                           AS subgrupo_produto,
       A.SITUACAO_PRODUTO_COMPRA             AS situacao_compra,
       F.PRODUTO_RESUMO                      AS produto_resumo,
       F.DESCRICAO                           AS produto_resumo_descricao,
       IIF(A.TIPO_PRECO = 1, 'false', 'true') AS preco_monitorado,
       A.CST_ORIGEM,
       A.GRUPO_TRIBUTARIO,
       A.GRUPO_TRIBUTARIO_ENTRADA,
       A.GRUPO_TRIBUTARIO_IMPORTADOS,
       A.NCM,
       A.CODIGO_CEST,
       A.CLASSE_PRODUTO,
       A.SECAO_PRODUTO,
       A.FABRICANTE_PRODUTO AS FABRICANTE,
       H.DESCRICAO AS CLASSE_PRODUTO_DESCRICAO,
       I.DESCRICAO AS SECAO_PRODUTO_DESCRICAO,
       J.DESCRICAO AS FABRICANTE_PRODUTO_DESCRICAO,
       ISNULL(A.MARCA, 0) AS MARCA,
       K.DESCRICAO        AS MARCA_DESCRICAO,
       PE.DIMENSAO_ALTURA,
       PE.DIMENSAO_PROFUNDIDADE,
       PE.DIMENSAO_LARGURA,
       PE.PESO_BRUTO,
       PE.PESO_LIQUIDO
FROM PRODUTOS                  A WITH(NOLOCK)
LEFT JOIN PRODUTOS_EAN         B WITH(NOLOCK) ON B.PRODUTO            = A.PRODUTO
                                             AND B.EAN_PRINCIPAL      = 'S'
LEFT JOIN FAMILIAS_PRODUTOS    C WITH(NOLOCK) ON C.FAMILIA_PRODUTO    = A.FAMILIA_PRODUTO
LEFT JOIN GRUPOS_PRODUTOS      D WITH(NOLOCK) ON D.GRUPO_PRODUTO      = A.GRUPO_PRODUTO
LEFT JOIN CATEGORIAS_PRODUTOS  E WITH(NOLOCK) ON E.CATEGORIA_PRODUTO  = A.CATEGORIA_PRODUTO
LEFT JOIN PRODUTOS_RESUMO      F WITH(NOLOCK) ON F.PRODUTO_RESUMO     = A.PRODUTO_RESUMO
LEFT JOIN SUBGRUPOS_PRODUTOS   G WITH(NOLOCK) ON A.SUBGRUPO_PRODUTO   = G.SUBGRUPO_PRODUTO
LEFT JOIN CLASSES_PRODUTOS     H WITH(NOLOCK) ON A.CLASSE_PRODUTO     = H.CLASSE_PRODUTO
LEFT JOIN SECOES_PRODUTOS      I WITH(NOLOCK) ON A.SECAO_PRODUTO      = I.SECAO_PRODUTO
LEFT JOIN FABRICANTES_PRODUTOS J WITH(NOLOCK) ON A.FABRICANTE_PRODUTO = J.FABRICANTE_PRODUTO
LEFT JOIN MARCAS               K WITH(NOLOCK) ON K.MARCA              = A.MARCA
LEFT JOIN PRODUTOS_ESPECIFICACOES PE WITH(NOLOCK) ON PE.PRODUTO = A.PRODUTO
ORDER BY A.PRODUTO;