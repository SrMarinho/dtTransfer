SELECT 
	L.CODEMP AS EMPRESA,
	L.CODFIL AS FILIAL,
	TO_CHAR(L.DATLCT, 'DD/MM/YYYY') AS DATA_LANCAMENTO,
	R.CTARED AS CONTA_REDUZIDA,
	P.DESCTA AS DESCR_CONTA_RDZ,
	CASE 
		WHEN R.DEBCRE = 'C' THEN SUM(r.VLRRAT) * -1
		WHEN R.DEBCRE = 'D' THEN SUM(r.VLRRAT) * 1
		ELSE SUM(r.VLRRAT) * 1
	END AS VALOR,	
	L.NUMLOT AS LOTE,
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
	AND P.GRUCTA IN (3,4)
	AND L.DATLCT BETWEEN TO_DATE('REPLACE_START_DATE', 'yyyy-mm-dd') AND TO_DATE('REPLACE_END_DATE', 'yyyy-mm-dd')
GROUP BY 
		L.CODEMP,
		L.CODFIL,
		TO_CHAR(L.DATLCT, 'DD/MM/YYYY'),
		R.CTARED,
		P.DESCTA,
		L.NUMLOT,
		r.CODCCU,
		c.DESCCU,
		R.DEBCRE
	ORDER BY 
		R.CTARED,
		R.CODCCU,
		L.CODFIL,
		TO_CHAR(L.DATLCT, 'DD/MM/YYYY')





