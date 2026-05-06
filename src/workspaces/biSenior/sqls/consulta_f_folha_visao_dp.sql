SELECT 
    F.NUMEMP AS empresa,
    Fc.CODFIL AS filial,
    F.TIPCOL AS tipo_colaborador,
    --fc.NUMCAD AS matricula,
    F.CODCAL AS cod_calculo,
    TO_CHAR(C.PERREF, 'MM/YYYY') AS periodo, 
    F.TABEVE AS tabela_eventos,
    F.CODEVE AS codigo_evento,
    EF.DESEVE AS nome_evento,
    F.ORIEVE AS origem,
    C.TIPCAL AS codigo_tipo_calculo,
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
    END AS nome_tipo_calculo,
    SUM(F.VALEVE) AS valor,
    F.refeve AS refeve,
    EF.CODCLC AS lig_contabil,
    cc.CODCCU AS custo,
    CC.NOMCCU AS descr_custo
FROM
    VETORH_PROD.R046VER F
INNER JOIN VETORH_PROD.R034fun fc ON
    fc.NUMEMP = f.NUMEMP
    AND fc.TIPCOL = f.TIPCOL 
    AND fc.NUMCAD = f.NUMCAD 
INNER JOIN VETORH_PROD.R044CAL C 
    ON C.NUMEMP = F.NUMEMP
    AND C.CODCAL = F.CODCAL
INNER JOIN VETORH_PROD.R008EVC EF 
    ON EF.CODEVE = F.CODEVE
    AND EF.CODTAB = F.TABEVE
INNER JOIN VETORH_PROD.R008INC IE 
    ON IE.CODTAB = EF.CODTAB 
    AND IE.CODEVE = EF.CODEVE
INNER JOIN VETORH_PROD.R018CCU CC ON
    CC.NUMEMP = F.NUMEMP 
    AND cc.CODCCU = fc.CODCCU 
WHERE F.TABEVE = 950
    AND F.NUMEMP IN (2, 5)
    AND F.TIPCOL = 1
    AND IE.NATRUB IN (1,1000,1002,1003,1016,1020,1022,1023,1201,1202,1203,1205,1206,1207,1210,1211,1225,1299,1350,1401,1406,1620,1629,1810,2930,9201,9216,9219,9908,9910,9989)
    AND Ie.CMPINC = (SELECT MAX(ie1.CMPINC) FROM VETORH_PROD.R008INC ie1 WHERE IE1.CODTAB = ie.CODTAB AND ie1.CODEVE = ie.CODEVE)
    -- AND C.PERREF BETWEEN ADD_MONTHS(SYSDATE, -12) AND SYSDATE
    AND C.PERREF >= TO_DATE('2023-01-01', 'yyyy-mm-dd')
GROUP BY
	F.NUMEMP,
	Fc.CODFIL,
	F.TIPCOL,
	F.CODCAL,
	TO_CHAR(C.PERREF, 'MM/YYYY'),
	F.TABEVE,
	F.CODEVE,
    EF.DESEVE,
    F.ORIEVE,
    C.TIPCAL,
    F.refeve,
    EF.CODCLC,
    cc.CODCCU,
    CC.NOMCCU
