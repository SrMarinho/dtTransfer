SELECT A.VENDEDOR AS codigo_gerente,
       A.NOME     AS nome_gerente
    FROM VENDEDORES A WITH(NOLOCK)
        WHERE A.CARGO_COMERCIAL = 6