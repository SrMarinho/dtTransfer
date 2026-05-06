SELECT A.PEDIDO_COMPRA_ENCERRAMENTO_PRODUTO AS id,
       A.PEDIDO_COMPRA_ENCERRAMENTO         AS pedido_compra_encerramento,
       A.PEDIDO_COMPRA                      AS pedido_compra,
       A.PRODUTO                            AS produto,
       A.QTDE_CONFIRMADA                    AS quantidade
    FROM PEDIDOS_COMPRAS_ENCERRAMENTO_PRODUTOS A