from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 
from config.databases.biMktNaz import BiMktNaz

class TitulosContasReceber(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.tableName = 'titulos_contas_receber'
    
    def getQuery(self) -> str:
        with open('sqls/consulta_titulos_contas_receber.sql', 'r') as file:
            return file.read()

    def deleteDay(self, startDate, endDate):
        logger.info(f"{self.tableName} - Apagando registros no dia {startDate}...")
        try:
            with self.toDriver.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM {} A WHERE A.entrada = '{}';".format(self.tableName, startDate))
                logger.info(f"Registros apagados com sucesso no dia {startDate} na tabela {self.tableName}!")
        except Exception as e:
            logger.info(f"{self.tableName} - Erro ao tentar apagar registros no dia {startDate}!")
            raise e

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS titulos_contas_receber
            (
                filial numeric(5,0),
                numero_titulo character varying(15),
                seq_mov numeric(4,0),
                tipo character varying(3),
                cliente numeric(9,0),
                nome_cliente character varying(100),
                emissao date,
                vencimento date,
                prov_pagamento date,
                ultimo_pagamento date,
                situacao character varying(2),
                forma_pagamento numeric(2,0),
                valor_original numeric(15,2),
                valor_aberto numeric(15,2),
                desconto numeric(15,2),
                total numeric(38,0),
                desc_forma_pgto character varying(30),
                entrada date,
                vcto_original date,
                modalidade character varying(3),
                filial_nfs numeric(5,0),
                serie_nfs character varying(3),
                nf_saida numeric(9,0),
                filial_nfentrada numeric(5,0),
                fornecedor_nfentrada numeric(9,0),
                serie_nfentrada character varying(3),
                grupo_empresa numeric(9,0),
                outros_descontos numeric(15,2),
                acrescimos numeric(15,2),
                juros_negociado numeric(15,2),
                multa_negociada numeric(15,2),
                descontos_negociados numeric(15,2),
                parcela_cartao numeric(4,0),
                autorizacao_tef character varying(100),
                numeracao_tef character varying(100),
                transacao character varying(5),
                tipo_transacao character varying(14),
                descricao character varying(60),
                portador character varying(4),
                nome_portador character varying(30),
                created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
                updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
            );
        """
