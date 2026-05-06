SELECT A.EMPRESA                      AS unidade,
       A.PEDIDO_COMPRA                AS pedido_compra,
       A.ENTIDADE                     AS entidade,
       CAST(A.DATA_HORA AS DATE)      AS data_pedido,
       CAST(A.DATA_ENTREGA AS DATE)   AS data_entrega,
       A.COMPRADOR                    AS cod_comprador,
       A.CONDICOES_PAGAMENTO          AS condicao_pagamento,
       A.TIPO_PEDIDO_COMPRA           AS tipo_pedido_compra,
       A.EMPRESA_DESTINO_CROSSDOCKING AS unidade_destino_crossdocking
    FROM PEDIDOS_COMPRAS A WITH(NOLOCK)