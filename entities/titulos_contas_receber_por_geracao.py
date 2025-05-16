
from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 
from config.databases.biMktNaz import BiMktNaz

class TitulosContasReceberPorGeracao(Queryable):
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
            'cnpj',
            'data_geracao'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_titulos_contas_receber_por_geracao.sql', 'r') as file:
            return file.read()

    def deleteDay(self, startDate, endDate):
        logger.info(f"{self.name} - Apagando registros no dia {startDate}...")
        try:
            with self.toDriver.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM {} A WHERE A.data_geracao = '{}';".format(self.name, startDate))
                logger.info(f"{self.name} - Registros apagados com sucesso no dia {startDate}!")
        except Exception as e:
            logger.info(f"{self.name} - Erro ao tentar apagar registros no dia {startDate}!")
            raise e

    def createTable(self):
        pass