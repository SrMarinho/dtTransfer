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
        self.name = 'titulos_contas_receber'
        self.columns = [
            'empresa',
            'filial',
            'numero_titulo',
            'seq_mov',
            'tipo',
            'cliente',
            'nome_cliente',
            'emissao',
            'vencimento',
            'prov_pagamento',
            'ultimo_pagamento',
            'situacao',
            'forma_pagamento',
            'valor_original',
            'valor_aberto',
            'desconto',
            'total',
            'desc_forma_pgto',
            'entrada',
            'vcto_original',
            'modalidade',
            'filial_nfs',
            'serie_nfs',
            'nf_saida',
            'filial_nfentrada',
            'fornecedor_nfentrada',
            'serie_nfentrada',
            'grupo_empresa',
            'outros_descontos',
            'acrescimos',
            'juros_negociado',
            'multa_negociada',
            'descontos_negociados',
            'parcela_cartao',
            'autorizacao_tef',
            'numeracao_tef',
            'transacao',
            'tipo_transacao',
            'descricao',
            'portador',
            'nome_portador',
            'cnpj'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_titulos_contas_receber.sql', 'r') as file:
            return file.read()

    def deleteDay(self, startDate, endDate):
        logger.info(f"{self.name} - Apagando registros no dia {startDate}...")
        try:
            with self.toDriver.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM {} A WHERE A.entrada = '{}';".format(self.name, startDate))
                logger.info(f"{self.name} - Registros apagados com sucesso no dia {startDate}!")
        except Exception as e:
            logger.info(f"{self.name} - Erro ao tentar apagar registros no dia {startDate}!")
            raise e

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS public.titulos_contas_receber
            (
                empresa integer,
                filial numeric(5,0),
                numero_titulo character varying(15),
                seq_mov numeric(4,0),
                tipo character varying(3) COLLATE pg_catalog."default",
                cliente numeric(9,0),
                nome_cliente character varying(100) COLLATE pg_catalog."default",
                emissao date,
                vencimento date,
                prov_pagamento date,
                ultimo_pagamento date,
                situacao character varying(2) COLLATE pg_catalog."default",
                forma_pagamento numeric(2,0),
                valor_original numeric(15,2),
                valor_aberto numeric(15,2),
                desconto numeric(15,2),
                total numeric(38,0),
                desc_forma_pgto character varying(30) COLLATE pg_catalog."default",
                entrada date,
                vcto_original date,
                modalidade character varying(3) COLLATE pg_catalog."default",
                filial_nfs numeric(5,0),
                serie_nfs character varying(3) COLLATE pg_catalog."default",
                nf_saida numeric(9,0),
                filial_nfentrada numeric(5,0),
                fornecedor_nfentrada numeric(9,0),
                serie_nfentrada character varying(3) COLLATE pg_catalog."default",
                grupo_empresa numeric(9,0),
                outros_descontos numeric(15,2),
                acrescimos numeric(15,2),
                juros_negociado numeric(15,2),
                multa_negociada numeric(15,2),
                descontos_negociados numeric(15,2),
                parcela_cartao numeric(4,0),
                autorizacao_tef character varying(100) COLLATE pg_catalog."default",
                numeracao_tef character varying(100) COLLATE pg_catalog."default",
                transacao character varying(5) COLLATE pg_catalog."default",
                tipo_transacao character varying(14) COLLATE pg_catalog."default",
                descricao character varying(60) COLLATE pg_catalog."default",
                portador character varying(4) COLLATE pg_catalog."default",
                nome_portador character varying(30) COLLATE pg_catalog."default",
                cnpj numeric(14, 0),
                created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
            )
        """
