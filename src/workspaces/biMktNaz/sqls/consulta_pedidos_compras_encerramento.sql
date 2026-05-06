SELECT A.PEDIDO_COMPRA_ENCERRAMENTO AS id,
       A.EMPRESA                    AS unidade,
       A.PEDIDO_COMPRA              AS pedido_compra,
       CAST(A.DATA_HORA AS DATE)    AS data_encerramento,
       A.FORNECEDOR                 AS entidade
    FROM PEDIDOS_COMPRAS_ENCERRAMENTO A;