SELECT produto,
       empresa,
       curva
    FROM VALOR_BASE WITH(NOLOCK)
        WHERE ANO = YEAR(GETDATE())
          AND MES = MONTH(GETDATE())
          AND empresa = empresa
    GROUP BY produto, empresa, curva
    ORDER BY produto
