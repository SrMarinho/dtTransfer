-- Não remover esses comandos
SET NOCOUNT ON
SET ANSI_WARNINGS OFF

  -------   Gera Tabela Temporária das Empresas do Usuário Logado   -------
if object_id('tempdb..#TEMP_EMPRESAS_USER') is not null
  DROP TABLE #TEMP_EMPRESAS_USER;
SELECT * INTO #TEMP_EMPRESAS_USER  FROM UDF_USUARIO_EMPRESAS('');   
  -------------------------------------------------------------------------
                                     
 --SET @EMPRESA = 999                                       
 --SET @DATA_INI = '01/03/2016'                                          
 --SET @DATA_FIM = '09/03/2016'   
                                                                        
if object_id('tempdb..#TIPO_ESTOQUE') is not null
DROP TABLE #TIPO_ESTOQUE;
                       
SELECT DISTINCT B.TIPO_ESTOQUE,A.CHECKOUT
INTO #TIPO_ESTOQUE
FROM WMS_CHECKOUT           A WITH(NOLOCK)
  JOIN #TEMP_EMPRESAS_USER    Y WITH(NOLOCK) ON Y.EMPRESA_USUARIA = A.EMPRESA
  JOIN WMS_CHECKOUT_RESUMO    C WITH(NOLOCK) ON C.CHECKOUT              = A.CHECKOUT
  JOIN ESTOQUE_TRANSFERENCIAS B WITH(NOLOCK) ON B.ESTOQUE_TRANSFERENCIA = C.ESTOQUE_TRANSFERENCIA
WHERE /*CONVERT (DATE,A.DATA_HORA,103) >= @DATA_INI
  AND CONVERT(DATE,A.DATA_HORA_CONFIRMACAO,103) <= @DATA_FIM
  AND*/ A.EMPRESA IN (SELECT EMPRESA FROM OS_EMPRESAS_CENTROS_ESTOQUES_MAPAS WHERE EMPRESA <= 19)
  AND A.CONFIRMAR <> 'N';
    

if object_id('tempdb..#CHECKOUT_TEMPOS') is not null
   DROP TABLE #CHECKOUT_TEMPOS;

SELECT A.CHECKOUT                      AS CHECKOUT,
       A.USUARIO_LOGADO                AS USUARIO_LOGADO,
       A.EMBALAGEM_SEPARACAO           AS EMBALAGEM_SEPARACAO, 
       Y.EMPRESA_USUARIA               AS Emp_CD,
       C.TIPO_ESTOQUE                  AS TIPO_ESTOQUE,
       A.DATA_HORA                     AS DATA_HORA_INI,
       A.DATA_HORA_CONFIRMACAO         AS DATA_HORA_FIM,
       A.VOLUMES                       AS VOLUMES,
      -- B.ESTOQUE_TRANSFERENCIA         AS ESTOQUE_TRANSFERENCIA,
       B.CENTRO_ESTOQUE_ORIGEM         AS EMPRESA,
       DATEDIFF(MINUTE, MIN(DATA_HORA), MAX(DATA_HORA_CONFIRMACAO) ) AS MINUTOS,
       SUM(B.QUANTIDADE)               AS SEPARADO
       
       INTO #CHECKOUT_TEMPOS
     
       FROM WMS_CHECKOUT          A WITH(NOLOCK)
       JOIN #TEMP_EMPRESAS_USER   Y WITH(NOLOCK) ON Y.EMPRESA_USUARIA = A.EMPRESA
       JOIN WMS_CHECKOUT_RESUMO   B WITH(NOLOCK) ON B.CHECKOUT = A.CHECKOUT
       JOIN #TIPO_ESTOQUE         C WITH(NOLOCK) ON C.CHECKOUT = A.CHECKOUT   

          
    GROUP BY A.CHECKOUT,
             USUARIO_LOGADO,
             EMBALAGEM_SEPARACAO,   
             Y.EMPRESA_USUARIA,
             DATA_HORA,
             DATA_HORA_CONFIRMACAO,
             B.CENTRO_ESTOQUE_ORIGEM,
            -- B.ESTOQUE_TRANSFERENCIA,
             A.VOLUMES,
             A.ENTIDADE,
             C.TIPO_ESTOQUE;


--PEGA OS TEMPOS DE SEPARAÇÃO--
if object_id('tempdb..#TRASNFERENCIAS_SEPARACOES_TEMPOS') is not null
   DROP TABLE #TRASNFERENCIAS_SEPARACOES_TEMPOS;


   SELECT A.CHECKOUT,
          USUARIO_LOGADO,
          EMBALAGEM_SEPARACAO,
          Emp_CD,
          A.TIPO_ESTOQUE,
          VOLUMES,
          SEPARADO,
          B.SEPARADOR,
                            
          MIN(B.DATA_HORA_INI_SEPARACAO) AS MENOR_DATA_HORA_INI_SEPARACAO,
          MAX(B.DATA_HORA_FIM_SEPARACAO) AS MAIOR_DATA_HORA_FIM_SEPARACAO,
          DATEDIFF( MINUTE, MIN(B.DATA_HORA_INI_SEPARACAO), MAX(B.DATA_HORA_FIM_SEPARACAO) ) AS MINUTOS
                                                    
          INTO #TRASNFERENCIAS_SEPARACOES_TEMPOS
    
    FROM #CHECKOUT_TEMPOS                     A WITH(NOLOCK)
    LEFT JOIN VW_CHECKOUT_TEMPOS_CONFERENCIAS_2 B WITH(NOLOCK) ON B.CHECKOUT = A.CHECKOUT


    GROUP BY USUARIO_LOGADO,
             VOLUMES,
             Emp_CD,
            -- A.ESTOQUE_TRANSFERENCIA,
             EMBALAGEM_SEPARACAO,
             EMPRESA,
             A.TIPO_ESTOQUE,
             A.CHECKOUT,
             SEPARADO,
             B.SEPARADOR;
            

--AGRUPA OS TEMPOS DE SEPARAÇÃO--
if object_id('tempdb..#METAS_CHECKOUT') is not null
   DROP TABLE #METAS_CHECKOUT;
  
   SELECT CHECKOUT,
          USUARIO_LOGADO,
          SEPARADOR,
          EMBALAGEM_SEPARACAO, 
          Emp_CD,
          TIPO_ESTOQUE,
          VOLUMES,
          SEPARADO,
          MENOR_DATA_HORA_INI_SEPARACAO,
          MAIOR_DATA_HORA_FIM_SEPARACAO,
          MINUTOS,
          MINUTOS / 60.00 AS HORAS

     INTO #METAS_CHECKOUT

   FROM  #TRASNFERENCIAS_SEPARACOES_TEMPOS;


SELECT A.CHECKOUT AS checkout,
      A.USUARIO_LOGADO AS operador,
      C.NOME AS nome,
      --A.SEPARADOR,
      -- D.NOME,
      EMBALAGEM_SEPARACAO AS embalagem_separacao,  
      Emp_CD AS emp_CD,
      --B.TIPO_EMBALAGEM,
      A.SEPARADO AS separado,
      --A.MINUTOS,
      /*ROUND(CASE WHEN ISNULL(A.HORAS,0) > 0
                  THEN A.SEPARADO / ISNULL (A.HORAS, 0)
                  ELSE 0
                  END,0)    AS MEDIA_POR_HORA,
                  
            --B.QUANTIDADE AS QTDE_META_HORA,
      
            CASE WHEN ISNULL(A.HORAS,0) > 0 
                THEN CONVERT(NUMERIC(15,2),((A.SEPARADO/A.HORAS) * 100 )/ B.QUANTIDADE)
                ELSE 0
          END              AS PERC_ATINGIDO,*/
          VOLUMES AS volumes,
          A.MENOR_DATA_HORA_INI_SEPARACAO AS menor_data_hora_ini_separacao,
          A.MAIOR_DATA_HORA_FIM_SEPARACAO AS maior_data_hora_fim_separacao
  FROM #METAS_CHECKOUT                  A WITH(NOLOCK)
  JOIN USUARIOS                         C WITH(NOLOCK) ON C.USUARIO            = A.USUARIO_LOGADO
  LEFT
  JOIN VW_WMS_METAS_CHECKOUT_OPERADOR   B WITH(NOLOCK) ON B.OPERADOR           = C.USUARIO
                                                      AND B.TIPO_EMBALAGEM     = A.TIPO_ESTOQUE
