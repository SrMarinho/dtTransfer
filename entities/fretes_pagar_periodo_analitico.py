from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class FretesPagarPeriodoAnalitico(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'fretes_pagar_periodo_analitico'
        self.columns = [
            'frete_pagar_transportadora', 'empresa', 'nome_empresa', 
            'transportadora', 'nome_transportadora', 'nota_despacho', 
            'num_romaneio', 'data_embarque', 'nf_faturamento', 
            'nf_numero', 'nf_serie', 'id_nota', 'entidade_cliente', 
            'nome_cliente', 'emissao_nf', 'data_bipagem', 'total_nf', 
            'total_produtos', 'volumes_nf', 'rota', 'frete_contrato', 
            'descricao_contrato', 'percentual_pagamento', 'tipo_calculo', 
            'valor_frete', 'id_autorizacao_pagamento', 'cont'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_fretes_pagar_periodo_analitico.sql', 'r') as file:
            return file.read()

    def deleteDay(self, startDate, endDate):
        logger.info(f"{self.name} - Apagando registros no dia {startDate}...")
        try:
            with self.toDriver.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"DELETE FROM {self.name} A WHERE A.data_embarque::DATE = '{startDate}'::DATE;")
                logger.info(f"{self.name} - Registros apagados com sucesso no dia {startDate}!")
        except Exception as e:
            logger.info(f"{self.name} - Erro ao tentar apagar registros no dia {startDate}!")
            raise e

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS public.fretes_pagar_periodo_analitico
            (
                frete_pagar_transportadora numeric(15,0),
                empresa numeric(15,0),
                nome_empresa character varying(72),
                transportadora numeric(15,0),
                nome_transportadora character varying(60),
                nota_despacho numeric(15,0),
                num_romaneio numeric(15,0),
                data_embarque timestamp without time zone,
                nf_faturamento numeric(15,0),
                nf_numero numeric(15,0),
                nf_serie character varying(3),
                id_nota character varying(100),
                entidade_cliente numeric(15,0),
                nome_cliente character varying(102),
                emissao_nf date,
                data_bipagem timestamp without time zone,
                total_nf numeric(15,2),
                total_produtos numeric(15,2),
                volumes_nf numeric(15,2),
                rota numeric(5,0),
                frete_contrato numeric(15,0),
                descricao_contrato character varying(256),
                percentual_pagamento numeric(10,2),
                tipo_calculo numeric(2,0),
                valor_frete numeric(15,2),
                id_autorizacao_pagamento numeric(15,0),
                cont integer
            );
        """
