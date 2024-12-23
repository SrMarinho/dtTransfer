from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 
from config.databases.biMktNaz import BiMktNaz

class TitulosContasPagar(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'titulos_contas_pagar'
        self.columns = [
            'empresa', 'titulo', 'seq_mov', 'tipo_titulo', 'fornecedor', 'cnpj_cpf_fornecedor',
            'filial', 'situacao', 'cfop', 'nf_entrada', 'chave_eletronica', 'vencimento',
            'ultimo_pagamento', 'entrada', 'valor_original', 'valor_aberto', 'valor_movimento',
            'nome_fornecedor', 'emissao', 'vencimento_original', 'data_movimento', 'data_pagamento',
            'juros', 'multa', 'encargos', 'acrescimos', 'descontos', 'outros_descontos',
            'grupo_empresa', 'transacao', 'tipo_transacao', 'descricao', 'serie_nf_entrada',
            'tipimp', 'tipo_imposto', 'per_desconto', 'portador', 'nome_portador',
            'cod_custo', 'descr_custo', 'valor_rateio', 'observacao', 'forn_compra'
        ]


    
    def getQuery(self) -> str:
        with open('sqls/consulta_titulos_contas_pagar.sql', 'r') as file:
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
            CREATE TABLE IF NOT EXISTS titulos_contas_pagar
            (
                empresa numeric(4,0),
                titulo character varying(15),
                seq_mov numeric(4,0),
                tipo_titulo character varying(3),
                fornecedor numeric(9,0),
                cnpj_cpf_fornecedor character varying(14),
                filial numeric(5,0),
                situacao character varying(2),
                cfop character varying(5),
                nf_entrada numeric(9,0),
                chave_eletronica character varying(50),
                vencimento timestamp without time zone,
                ultimo_pagamento timestamp without time zone,
                entrada timestamp without time zone,
                valor_original numeric(15,2),
                valor_aberto numeric(15,2),
                nome_fornecedor character varying(100),
                emissao timestamp without time zone,
                vencimento_original timestamp without time zone,
                juros numeric(15,2),
                multa numeric(15,2),
                encargos numeric(15,2),
                acrescimos numeric(15,2),
                descontos numeric(15,2),
                outros_descontos numeric(15,2),
                grupo_empresa numeric(9,0),
                transacao character varying(5),
                tipo_transacao character varying(14),
                descricao character varying(60),
                serie_nf_entrada character varying(3),
                tipimp numeric(2,0),
                tipo_imposto character varying(59),
                per_desconto numeric(5,2),
                portador character varying(4),
                nome_portador character varying(30),
                created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
                updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
            );
        """
