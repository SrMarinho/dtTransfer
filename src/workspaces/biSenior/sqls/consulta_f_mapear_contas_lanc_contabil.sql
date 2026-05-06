	SELECT
		P.GRUCTA AS GRUPO,
		L.CODEMP AS EMPRESA,
		L.CODFIL AS FILIAL,
		CASE 
			WHEN ((L.CTACRE = 515) OR (L.CTADEB = 515)) THEN TO_CHAR(L.DATLCT, 'yyyy-mm-dd')
			ELSE TO_CHAR(TRUNC(L.DATLCT,'MM'), 'yyyy-mm-dd')
		END AS DATA_LANCAMENTO,
		R.CTARED AS CONTA_REDUZIDA,
		P.DESCTA AS DESCR_CONTA_RDZ,
		CASE 
			WHEN R.DEBCRE = 'C' THEN SUM(r.VLRRAT) * -1
			WHEN R.DEBCRE = 'D' THEN SUM(r.VLRRAT) * 1
			ELSE SUM(r.VLRRAT) * 1
		END AS VALOR,
		CASE
			WHEN ((L.CTACRE = 515) OR (L.CTADEB = 515)) THEN L.NUMLOT
			ELSE 0
		END AS LOTE,
		L.ORILCT AS ORIGEM,
		CASE 
			WHEN L.ORILCT = 'MAN' THEN 'Manual'
			WHEN L.ORILCT = 'VEN' THEN 'Mercado-NF Saidas'
			WHEN L.ORILCT = 'VEF' THEN 'Mercado-Faturas'
			WHEN L.ORILCT = 'EST' THEN 'Estoques-Movimentos'
			WHEN L.ORILCT = 'REC' THEN 'Contas Receber-Movimentos'
			WHEN L.ORILCT = 'AFR' THEN 'Contas Receber-Ajuste Financeiro'
			WHEN L.ORILCT = 'RAM' THEN 'Contas Receber-Auste Valor de Mercado'
			WHEN L.ORILCT = 'ARV' THEN 'Contas Receber-Variacao Cambial'
			WHEN L.ORILCT = 'CPR' THEN 'Suprimentos-NF Entradas'
			WHEN L.ORILCT = 'COF' THEN 'Suprimentos-Faturas'
			WHEN L.ORILCT = 'PAG' THEN 'Contas Pagar-Movimentos'
			WHEN L.ORILCT = 'COM' THEN 'Contas Pagar-Comissoes'
			WHEN L.ORILCT = 'AFP' THEN 'Contas Pagar-Ajuste Financeiro'
			WHEN L.ORILCT = 'PAM' THEN 'Contas Pagar-Ajuste Valor de Mercado'
			WHEN L.ORILCT = 'APV' THEN 'Contas Pagar-Variacao Cambial'
			WHEN L.ORILCT = 'TES' THEN 'Tesouraria'
			WHEN L.ORILCT = 'PRD' THEN 'Producao'
			WHEN L.ORILCT = 'PAT' THEN 'Patrimonio'
			WHEN L.ORILCT = 'IVE' THEN 'Tributos-Vendas'
			WHEN L.ORILCT = 'ICO' THEN 'Tributos-Compras'
			WHEN L.ORILCT = 'IVZ' THEN 'Tributos-ReducaoZ'
			WHEN L.ORILCT = 'IOD' THEN 'Tributos-Outros Documentos'
			WHEN L.ORILCT = 'IMP' THEN 'Tributos-Apuracao/Calculos'
			WHEN L.ORILCT = 'RPA' THEN 'Tributos-Recibo de Pagamento Autonomo'
			WHEN L.ORILCT = 'UIV' THEN 'Tributos-Unidade Imobiliaria Vendida'
			WHEN L.ORILCT = 'IVR' THEN 'Tributos-Unidade Imobiliaria Vendida-Valores Recebidos'
			WHEN L.ORILCT = 'IVO' THEN 'Tributos-Unidade Imobiliaria Vendida-Custo Orçado'
			WHEN L.ORILCT = 'IVI' THEN 'Tributos-Unidade Imobiliaria Vendida-Custo Incorrido'
			WHEN L.ORILCT = 'PRJ' THEN 'Projetos-Lançamentos Manuais'
			WHEN L.ORILCT = 'CTC' THEN 'Cota Capital-Movimentos'
			WHEN L.ORILCT = 'VRB' THEN 'Vetorh-FP'
			WHEN L.ORILCT = 'REG' THEN 'Regente'
		END AS DESCR_ORIGEM,
		r.CODCCU AS cod_custo,
		c.DESCCU AS descr_custo,
		R.DEBCRE AS DEB_CRED
	FROM
		SAPIENS_PROD.E640LCT L
	LEFT JOIN SAPIENS_PROD.E640RAT R ON
		R.CODEMP = L.CODEMP
		AND R.NUMLCT = L.NUMLCT
	LEFT JOIN SAPIENS_PROD.E044CCU C ON
		C.CODEMP = R.CODEMP
		AND C.CODCCU = R.CODCCU
	INNER JOIN SAPIENS_PROD.E045PLA P ON
		P.CODEMP = L.CODEMP 
		AND P.CTARED = R.CTARED 
	WHERE
		L.CODEMP IN (2, 5)
		AND L.SITLCT = 2
		AND P.GRUCTA = 3
		AND L.DATLCT >= TO_DATE('REPLACE_START_DATE', 'yyyy-mm-dd')
		AND L.DATLCT < TO_DATE('REPLACE_END_DATE', 'yyyy-mm-dd')
	GROUP BY 
			P.GRUCTA,
			L.CODEMP,
			L.CODFIL,
			L.DATLCT,
			R.CTARED,
			P.DESCTA,
			L.CTACRE,
			l.CTADEB,
			L.NUMLOT,
			L.ORILCT,
			r.CODCCU,
			c.DESCCU,
			R.DEBCRE

UNION ALL 

	SELECT
		P.GRUCTA AS GRUPO,
		L.CODEMP AS EMPRESA,
		L.CODFIL AS FILIAL,
		CASE
			WHEN (L.CTADEB IN (528,532,575)) OR  (L.CTACRE IN (528,532,575)) THEN TO_CHAR(TRUNC(L.DATLCT,'MM'), 'yyyy-mm-dd')
			ELSE TO_CHAR(L.DATLCT, 'yyyy-mm-dd')
		END AS DATA_LANCAMENTO,
		R.CTARED AS CONTA_REDUZIDA,
		P.DESCTA AS DESCR_CONTA_RDZ,
		CASE 
			WHEN R.DEBCRE = 'C' THEN SUM(r.VLRRAT) * -1
			WHEN R.DEBCRE = 'D' THEN SUM(r.VLRRAT) * 1
			ELSE SUM(r.VLRRAT) * 1
		END AS VALOR,
		CASE
			WHEN (L.CTADEB IN (528,532,575)) OR  (L.CTACRE IN (528,532,575)) THEN 0 
			ELSE L.NUMLOT
		END AS LOTE,
		L.ORILCT AS ORIGEM,
		CASE 
			WHEN L.ORILCT = 'MAN' THEN 'Manual'
			WHEN L.ORILCT = 'VEN' THEN 'Mercado-NF Saidas'
			WHEN L.ORILCT = 'VEF' THEN 'Mercado-Faturas'
			WHEN L.ORILCT = 'EST' THEN 'Estoques-Movimentos'
			WHEN L.ORILCT = 'REC' THEN 'Contas Receber-Movimentos'
			WHEN L.ORILCT = 'AFR' THEN 'Contas Receber-Ajuste Financeiro'
			WHEN L.ORILCT = 'RAM' THEN 'Contas Receber-Auste Valor de Mercado'
			WHEN L.ORILCT = 'ARV' THEN 'Contas Receber-Variacao Cambial'
			WHEN L.ORILCT = 'CPR' THEN 'Suprimentos-NF Entradas'
			WHEN L.ORILCT = 'COF' THEN 'Suprimentos-Faturas'
			WHEN L.ORILCT = 'PAG' THEN 'Contas Pagar-Movimentos'
			WHEN L.ORILCT = 'COM' THEN 'Contas Pagar-Comissoes'
			WHEN L.ORILCT = 'AFP' THEN 'Contas Pagar-Ajuste Financeiro'
			WHEN L.ORILCT = 'PAM' THEN 'Contas Pagar-Ajuste Valor de Mercado'
			WHEN L.ORILCT = 'APV' THEN 'Contas Pagar-Variacao Cambial'
			WHEN L.ORILCT = 'TES' THEN 'Tesouraria'
			WHEN L.ORILCT = 'PRD' THEN 'Producao'
			WHEN L.ORILCT = 'PAT' THEN 'Patrimonio'
			WHEN L.ORILCT = 'IVE' THEN 'Tributos-Vendas'
			WHEN L.ORILCT = 'ICO' THEN 'Tributos-Compras'
			WHEN L.ORILCT = 'IVZ' THEN 'Tributos-ReducaoZ'
			WHEN L.ORILCT = 'IOD' THEN 'Tributos-Outros Documentos'
			WHEN L.ORILCT = 'IMP' THEN 'Tributos-Apuracao/Calculos'
			WHEN L.ORILCT = 'RPA' THEN 'Tributos-Recibo de Pagamento Autonomo'
			WHEN L.ORILCT = 'UIV' THEN 'Tributos-Unidade Imobiliaria Vendida'
			WHEN L.ORILCT = 'IVR' THEN 'Tributos-Unidade Imobiliaria Vendida-Valores Recebidos'
			WHEN L.ORILCT = 'IVO' THEN 'Tributos-Unidade Imobiliaria Vendida-Custo Orçado'
			WHEN L.ORILCT = 'IVI' THEN 'Tributos-Unidade Imobiliaria Vendida-Custo Incorrido'
			WHEN L.ORILCT = 'PRJ' THEN 'Projetos-Lançamentos Manuais'
			WHEN L.ORILCT = 'CTC' THEN 'Cota Capital-Movimentos'
			WHEN L.ORILCT = 'VRB' THEN 'Vetorh-FP'
			WHEN L.ORILCT = 'REG' THEN 'Regente'
		END AS DESCR_ORIGEM,
		r.CODCCU AS cod_custo,
		c.DESCCU AS descr_custo,
		R.DEBCRE AS DEB_CRED
	FROM
		SAPIENS_PROD.E640LCT L
	LEFT JOIN SAPIENS_PROD.E640RAT R ON
		R.CODEMP = L.CODEMP
		AND R.NUMLCT = L.NUMLCT
	LEFT JOIN SAPIENS_PROD.E044CCU C ON
		C.CODEMP = R.CODEMP
		AND C.CODCCU = R.CODCCU
	INNER JOIN SAPIENS_PROD.E045PLA P ON
		P.CODEMP = L.CODEMP 
		AND P.CTARED = R.CTARED 
	WHERE
		L.CODEMP IN (2, 5)
		AND L.SITLCT = 2
		AND P.GRUCTA = 4
		AND L.DATLCT >= TO_DATE('REPLACE_START_DATE', 'yyyy-mm-dd')
		AND L.DATLCT < TO_DATE('REPLACE_END_DATE', 'yyyy-mm-dd')
	GROUP BY 
			P.GRUCTA,
			L.CODEMP,
			L.CODFIL,
			L.DATLCT,
			R.CTARED,
			P.DESCTA,
			L.CTACRE,
			l.CTADEB,
			L.NUMLOT,
			L.ORILCT,
			r.CODCCU,
			c.DESCCU,
			R.DEBCRE
	
		
		