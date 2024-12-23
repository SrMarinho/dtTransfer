from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 


class FFolhaVisaoDp(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'f_folha_visao_dp'
        self.columns = (
            'empresa', 'filial', 'tipo_colaborador', 'cod_calculo', 'periodo', 'tabela_eventos', 'codigo_evento', 
            'nome_evento', 'origem', 'codigo_tipo_calculo', 'nome_tipo_calculo', 'valor', 'refeve', 
            'lig_contabil', 'custo', 'descr_custo'
        )

    
    def getQuery(self) -> str:
        with open('sqls/consulta_f_folha_visao_dp.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS f_folha_visao_dp
            (
                empresa numeric(4,0),
                filial numeric(6,0),
                tipo_colaborador numeric(1,0),
                cod_calculo numeric(5,0),
                periodo character varying(7),
                tabela_eventos numeric(3,0),
                codigo_evento numeric(4,0),
                nome_evento character varying(25),
                origem character varying(1),
                codigo_tipo_calculo numeric(2,0),
                nome_tipo_calculo character varying(31),
                valor numeric(11,2),
                refeve numeric(11,2),
                lig_contabil numeric(4,0),
                custo character varying(18),
                descr_custo character varying(80),
                created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
            );
        """
