from config.databases.biMktNaz import BiMktNaz
from config.databases.PBS_NAZARIA_DADOS import PbsNazariaDados
from config.databases.Senior import Senior

class DatabaseFactory:
    @staticmethod
    def getInstance(name):
        databases_instances = {
            'PbsNazariaDados': PbsNazariaDados,
            'biMktNaz': BiMktNaz,
            'Senior': Senior
        }
        if name in databases_instances:
            return databases_instances[name]()
        raise "Banco de dados não encontrado!"
