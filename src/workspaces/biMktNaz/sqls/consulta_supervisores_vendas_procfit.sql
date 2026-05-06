SELECT A.VENDEDOR         AS codigo_supervisor,
       A.NOME             AS nome_supervisor,
       A.ENTIDADE_GERENTE AS codigo_gerente
   FROM VENDEDORES A WITH(NOLOCK)
       WHERE A.CARGO_COMERCIAL = 1
