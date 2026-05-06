SELECT
	A.CONDICAO_PAGAMENTO as condicao_pagamento,
	A.DESCRICAO as descricao,
	A.VENDA as venda,
	A.COMPRA as compra,
	A.VALIDAR_LIMITE as validar_limite,
	A.SIGLA as sigla,
	A.TIPO_CONDICAO_PAGAMENTO as tipo_condicao_pagamento
FROM
	CONDICOES_PAGAMENTO	A