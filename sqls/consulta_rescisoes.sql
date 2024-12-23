--------------------Consulta Rescisões------------------------

SELECT DISTINCT 
	A.NUMEMP AS EMPRESA,
	A.NUMCAD AS MATRICULA,
	TO_CHAR(RCM.DATDEM, 'DD/MM/YYYY')  AS DATA_DEMISSAO,
	RCM.CAUDEM AS COD_CAUSA,
	CAU.DESDEM AS DESCR_CAUSA,
	RMD.CODRMD AS COD_MOTIVO,
	RMD.DESRMD AS DESCR_MOTIVO,
	RCM.SLDFGT AS SALDO_FGTS,
	RCM.TOTPRO AS TOTAL_PROVENTOS_RESC,
	RCM.TOTDES AS TOTAL_DESCONTO_RESC,
	(RCM.TOTPRO - RCM.TOTDES) AS TOTAL_LIQ_RESC,
	TO_CHAR(RCS.DATPAG,'DD/MM/YYYY')  AS DATA_DISSIDIO,
	rcs.TOTPRO AS TOTAL_PROVENTOS_RESC_COMPL,
	rcs.TOTDES AS TOTAL_DESCONTO_RESC_COMPL,
	(rcs.TOTPRO - rcs.TOTDES) AS TOTAL_LIQ_RESC_DISSIDIO
FROM VETORH_PROD.R034FUN A
 LEFT JOIN VETORH_PROD.R042RCM RCM ---Rescisao mestre
 		 ON RCM.NUMEMP = A.NUMEMP
 		AND RCM.TIPCOL = A.TIPCOL 
 		AND RCM.NUMCAD = A.NUMCAD
 LEFT JOIN VETORH_PROD.R042RCS RCS ---Rescisao complementar 
 		 ON RCS.NUMEMP = A.NUMEMP 
 		AND RCS.TIPCOL = A.TIPCOL 
 		AND RCS.NUMCAD = A.NUMCAD
 LEFT JOIN VETORH_PROD.R042CAU CAU --causa da demissão
         ON CAU.CAUDEM = RCM.CAUDEM 
 LEFT JOIN VETORH_PROD.R114RMD RMD ---motivo da demissão
 		 ON RMD.CODRMD = RCM.CODRMD
      WHERE A.NUMEMP IN (2, 5)
        AND A.TIPCOL = 1
        AND A.SITAFA = 7
        --  AND DATDEM BETWEEN TO_DATE('REPLACE_START_DATE', 'yyyy-mm-dd') AND TO_DATE('REPLACE_END_DATE', 'yyyy-mm-dd')
 
