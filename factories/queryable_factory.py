from entities.titulos_com_notas import TitulosComNotas
from entities.regras_excessao_sku_regra import RegrasExcessaoSkuRegra

class QueryableFactory:
    def __init__(self):
        ...

    @staticmethod
    def getInstance(queryName, params):
        entities_list = {
            'regras_excessao_sku_regra': RegrasExcessaoSkuRegra,
            'titulos_com_notas': TitulosComNotas
        }

        if queryName in entities_list:
            return entities_list[queryName](params)
        else:
            raise "Tabela não registrada!"
