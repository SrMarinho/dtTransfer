from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class NfCompra(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'nf_compra'
        self.columns = [
            'unidade', 
            'nf_compra', 
            'nf_numero', 
            'pedido_compra', 
            'entidade', 
            'data_emissao', 
            'data_entrada', 
            'chave_nfe', 
            'dias'
        ]
    
    def getQuery(self) -> str:
        try:
            with open('sqls/consulta_nf_compra.sql', 'r') as file:
                return file.read()
        except Exception as e:
            raise e

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS nf_compra
            (
                nf_compra numeric(15,0) NOT NULL,
                unidade numeric(15,0) NOT NULL,
                nf_numero numeric(10,0),
                pedido_compra numeric(15,0),
                entidade numeric(15,0),
                data_emissao date NOT NULL,
                data_entrada date,
                chave_nfe character varying(50) COLLATE pg_catalog."default",
                condicoes_pagamento numeric(15,0)
            )
        """
