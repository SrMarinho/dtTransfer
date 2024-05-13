-------------------FOLHA PAGAMENTO PARA RECURSOS HUMANOS---------------------
SELECT  
	F.NUMEMP AS EMPRESA,
	FUN.CODFIL AS FILIAL,
	F.TIPCOL AS TIPO_COLABORADOR,
	F.CODCAL AS COD_CALCULO,
	TO_CHAR(C.PERREF, 'MM/YYYY') AS PERIODO, 
	F.TABEVE AS TABELA_EVENTOS,
	F.CODEVE AS CODIGO_EVENTO,
	EF.DESEVE AS NOME_EVENTO,
	F.ORIEVE AS ORIGEM,
	C.TIPCAL AS CODIGO_TIPO_CALCULO,
	CASE 
		WHEN C.TIPCAL = 11 THEN 'Calculo Mensal'
		WHEN C.TIPCAL = 12 THEN 'Folha Complementar'
		WHEN C.TIPCAL = 13 THEN 'Complementar de Dissidio'
		WHEN C.TIPCAL = 14 THEN 'Pagamento de Dissidio'
		WHEN C.TIPCAL = 15 THEN 'Complementar Rescisao'
		WHEN C.TIPCAL = 21 THEN 'Primeira Semana'
		WHEN C.TIPCAL = 22 THEN 'Semana Intermediaria'
		WHEN C.TIPCAL = 23 THEN 'Ultima Semana'
		WHEN C.TIPCAL = 31 THEN 'Adiantamento 13º Salario'
		WHEN C.TIPCAL = 32 THEN '13º Salario Integral'
		WHEN C.TIPCAL = 41 THEN 'Primeira Quinzena'
		WHEN C.TIPCAL = 42 THEN 'Segunda Quinzena'
		WHEN C.TIPCAL = 91 THEN 'Adiantamento Salarial'
		WHEN C.TIPCAL = 92 THEN 'Participacao nos Lucros'
		WHEN C.TIPCAL = 93 THEN 'Especiais'
		WHEN C.TIPCAL = 94 THEN 'Reclamatoria Trabalhista'
		ELSE 'Nao informado o tipo de calculo'
	END AS NOME_TIPO_CALCULO,
	F.VALEVE AS VALOR,
	F.REFEVE AS PERIODO_EVE,
	EF.CODCLC AS LIQ_CONTABIL
FROM
	R046VER F
LEFT JOIN R038HFI FUN 
		ON FUN.NUMEMP = F.NUMEMP 
	   AND FUN.TIPCOL = F.TIPCOL 
	   AND FUN.NUMCAD = F.NUMCAD
INNER JOIN R044CAL C 
		ON C.NUMEMP = F.NUMEMP
	   AND C.CODCAL = F.CODCAL
INNER JOIN R008EVC EF 
		ON EF.CODEVE = F.CODEVE
	   AND EF.CODTAB = F.TABEVE
INNER JOIN R008INC IE 
		ON IE.CODTAB = EF.CODTAB 
	   AND IE.CODEVE = EF.CODEVE  
WHERE F.TABEVE = 950
	AND F.NUMEMP IN (2, 5)
	AND F.TIPCOL = 1
	AND IE.NATRUB IN (1,1000,1002,1003,1016,1020,1022,1023,1201,1202,1203,1205,1206,1207,1210,1211,1225,1299,1350,1401,1406,1620,1629,1810,2930,9201,9216,9219,9908,9910,9989)
	AND C.PERREF TO_CHAR(TO_DATE('REPLACE_START_DATE', 'YYYY-MM-DD'), 'MM/YYYY')
--	AND C.FIMCMP <= :DATAFIM;