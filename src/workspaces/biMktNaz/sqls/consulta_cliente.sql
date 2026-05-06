SELECT A.ENTIDADE                         AS codigo_cliente,
       DBO.SO_NUMERO(ISNULL(A.INSCRICAO_FEDERAL, '?')) AS cnpj,
       A.NOME                             AS razao_social,
       A.NOME_FANTASIA                    AS nome_fantasia,
       ISNULL(B.CLIENTE_REDE, 9999)       AS codigo_rede,
       C.DESCRICAO                        AS rede,
       ISNULL(B.GRUPO_CLIENTE,88)         AS codigo_grupo_cliente,
       D.DESCRICAO                        AS grupo_cliente,
       ISNULL(E.ENDERECO, '?')                         AS endereco,
       ISNULL(E.BAIRRO, '?')                           AS bairro,
       DBO.SO_NUMERO(ISNULL(E.CEP, '?'))               AS cep,
       ISNULL(E.CIDADE, '?')                           AS cidade,
       ISNULL(E.ESTADO, '?')                           AS estado,
       ISNULL((SELECT TOP 1 CONCAT(Z.DDD, Z.NUMERO)
            FROM TELEFONES Z WITH(NOLOCK)
        WHERE Z.ENTIDADE = A.ENTIDADE), '?')    AS telefone,
       ISNULL((SELECT TOP 1 Z.EMAIL
            FROM EMAIL Z WITH(NOLOCK)
        WHERE Z.ENTIDADE = A.ENTIDADE), '?')    AS email,
       E.CODIGO_IBGE                            AS codigo_ibge
    FROM ENTIDADES                                A WITH(NOLOCK)
    LEFT JOIN PEDIDOS_VENDAS_PARAMETROS_ENTIDADES B WITH(NOLOCK) ON B.ENTIDADE      = A.ENTIDADE
    LEFT JOIN CLIENTES_REDES                      C WITH(NOLOCK) ON C.CLIENTE_REDE  = ISNULL(B.CLIENTE_REDE, 9999)
    LEFT JOIN GRUPOS_CLIENTES                     D WITH(NOLOCK) ON D.GRUPO_CLIENTE = ISNULL(B.GRUPO_CLIENTE,88)
    LEFT JOIN ENDERECOS                           E WITH(NOLOCK) ON E.ENTIDADE      = A.ENTIDADE
WHERE
    A.INSCRICAO_FEDERAL IS NOT NULL
        ORDER BY A.ENTIDADE
