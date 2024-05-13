SELECT 
	TO_CHAR(M.DATMOV,'DD/MM/YYYY')  AS DATA_MOVIMENTACAO,
	M.CODEMP AS EMPRESA,
	M.CODFIL AS FILIAL,
	F.SIGFIL AS DESCR_FILIAL,
	M.FILDEP AS FILIAL_DEP,
	M.NUMEME AS NUM_REQUISICAO,
	R.CODPRO AS PRODUTO,
	P.DESPRO AS DESCR_PRODUTO,
	R.CODDER AS DERIVACAO,
	D.DESDER AS DESCR_DERIVACAO,
	P.UNIMED AS UNIDADE_MEDIDA,
	M.QTDMOV AS QUANTIDADE,
	P.CODFAM AS FAMILIA_PROD,
	FAM.DESFAM AS DESC_FAMILIA,
	R.CTARED AS CODRED,
	PLA.DESCTA AS DESCR_CODRED,
	R.VLRRAT AS VALOR_RATEIO,
	R.CODCCU AS COD_CUSTO,
	C.DESCCU AS DESCR_CUSTO,
	M.NUMLOT AS LOTE_CONTABIL,
	M.USURES AS COD_USUARIO,
	U.NOMUSU AS NOME_USUARIO
FROM SAPIENS_PROD.E210MVP M
	INNER JOIN SAPIENS_PROD.E210RAT R
			ON R.CODEMP = M.CODEMP 
		   AND R.CODPRO = M.CODPRO 
		   AND R.CODDER = M.CODDER 
		   AND R.DATMOV = M.DATMOV
		   AND R.SEQMOV = M.SEQMOV 
	INNER JOIN SAPIENS_PROD.E045PLA PLA 
			ON PLA.CODEMP = R.CODEMP 
		   AND PLA.CTARED = R.CTARED
	INNER JOIN SAPIENS_PROD.E001TNS T 
			ON T.CODEMP = M.CODEMP
		   AND T.CODTNS = M.CODTNS
	INNER JOIN SAPIENS_PROD.E075PRO P
			ON P.CODEMP = M.CODEMP
		   AND P.CODPRO = M.CODPRO
	INNER JOIN SAPIENS_PROD.E012FAM FAM
			ON FAM.CODEMP = P.CODEMP
		   AND FAM.CODFAM = P.CODFAM
	INNER JOIN SAPIENS_PROD.E075DER D 
			ON D.CODEMP = M.CODEMP 
		   AND D.CODPRO = M.CODPRO 
		   AND D.CODDER = M.CODDER
	INNER JOIN SAPIENS_PROD.E070FIL F
			ON F.CODEMP = M.CODEMP 
		   AND F.CODFIL = M.CODFIL
	INNER JOIN SAPIENS_PROD.E070EMP E 
			ON E.CODEMP = M.CODEMP 
	INNER JOIN SAPIENS_PROD.E044CCU C
			ON C.CODEMP = R.CODEMP 
		   AND C.CODCCU = R.CODCCU 
	INNER JOIN SAPIENS_PROD.E099USU U
			ON U.CODEMP = M.CODEMP 
		   AND U.CODUSU = M.USURES 
WHERE
	M.CODEMP IN (2, 5)--:CODEMP
	AND M.DATMOV >= TO_DATE('2024-01-01', 'yyyy-mm-dd')
	AND M.DATMOV BETWEEN TO_DATE('REPLACE_START_DATE', 'yyyy-mm-dd') AND TO_DATE('REPLACE_END_DATE', 'yyyy-mm-dd')
	AND M.CODTNS <> ' '
	AND R.CODPRO LIKE 'S%'
ORDER BY
	M.DATMOV,
	M.CODFIL
	
