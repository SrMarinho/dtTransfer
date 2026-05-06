SELECT
    nc.EMPRESA                          AS unidade,
    nc.NF_COMPRA                        AS nf_compra,
    nc.NF_NUMERO                        AS nf_numero,
    nc.PEDIDO_COMPRA                    AS pedido_compra,
    nc.ENTIDADE                         AS entidade,
    CAST(nc.EMISSAO AS DATE)            AS data_emissao,
    CAST(nc.DATA_PROCESSAMENTO AS DATE) AS data_entrada,
    nc.CHAVE_NFE                        AS chave_nfe,
	NCP.DIAS                            AS dias
FROM 
	NF_COMPRA nc WITH(NOLOCK)
	LEFT JOIN NF_COMPRA_PARCELAS ncp WITH(NOLOCK) ON ncp.NF_COMPRA = nc.NF_COMPRA