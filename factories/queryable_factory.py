from entities.venda import Venda

class QueryableFactory:
    def __init__(self):
        ...

    @staticmethod
    def getInstance(queryName):
        entities_list = {
            'venda': Venda
        }

        return entities_list[queryName]() if queryName in entities_list else None
