-------------------FOLHA PAGAMENTO PARA CONTROLADORIA---------------------
SELECT 
	C.NUMEMP AS EMPRESA,
	C.CODFIL AS FILIAL,
	F.NOMFIL AS NOME_FILIAL,
	TO_CHAR(C.DATLAN,'dd/mm/yyyy')  AS DATA_LANCAMENTO,
	C.OPCCTB AS cod_OPCAO_CONTABILIDADE,
	CASE 
		WHEN C.OPCCTB = 1 THEN 'Folha Mensal'
		WHEN C.OPCCTB = 2 THEN 'Ferias'
		WHEN C.OPCCTB = 3 THEN 'Provisao'
		WHEN C.OPCCTB = 4 THEN 'Rescisao'
		WHEN C.OPCCTB = 5 THEN 'Pagtos Terceiros'
		WHEN C.OPCCTB = 6 THEN 'Pagtos Pessoa Juridica'
		WHEN C.OPCCTB = 7 THEN 'Pagtos Producao Fisica'
		WHEN C.OPCCTB = 8 THEN 'Pagtos Producao Juridica'
		WHEN C.OPCCTB = 9 THEN 'Compensacoes'
		ELSE 'Sem definicao'
	END AS OPCAO_CONTABILIDADE,
	C.HISPAD AS COD_HISTORICO,
	C.VALLAN AS VALOR,
	C.CODCCU AS COD_CUSTO,
	CC.NOMCCU AS DESCR_CUSTO,
	C.REDDEB AS CODRED_DEBITO,
	C.REDCRE AS CODRED_CREDITO,
	CLC.NOMCON AS DESCR_COD_LIG_CONTA_CONTABIL,
	C.DEBCRE,
	C.CODLOT AS LOTE_CONTABIL
FROM VETORH_PROD.R048CTB C
	INNER JOIN VETORH_PROD.R048CLB CLB
	        ON CLB.TABEVE = C.TABEVE 
	       AND CLB.CODCLC = C.CLCPDB 
	INNER JOIN VETORH_PROD.R048CLC CLC
			ON CLC.TABEVE = CLB.TABEVE 
		   AND CLC.TABEVE = C.TABEVE 
		   AND CLC.CODCLC = CLB.CODCLC 
	INNER JOIN VETORH_PROD.R044CAL FF
			ON FF.NUMEMP = C.NUMEMP 
		   AND FF.CODCAL = C.CODCAL
 	INNER JOIN VETORH_PROD.R030FIL F 
			ON F.NUMEMP = C.NUMEMP 
		   AND F.CODFIL = C.CODFIL
	 LEFT JOIN VETORH_PROD.R018CCU CC
	 		ON CC.NUMEMP = C.NUMEMP 
	 	   AND CC.CODCCU = C.CODCCU
WHERE C.TABEVE = 950
AND C.NUMEMP = 5
AND C.CONGER <> 0
AND C.DATLAN BETWEEN TO_DATE('REPLACE_START_DATE', 'yyyy-mm-dd') AND TO_DATE('REPLACE_END_DATE', 'yyyy-mm-dd')
