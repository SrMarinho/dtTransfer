from processes.ndays_ago import nDaysAgo
from processes.regular_query import RegularQuery
from config.logger.logging import logger

class ProcessFactory:
    @staticmethod
    def getInstance(name, params):
        processes_instances = {
            'regular': RegularQuery,
            'nDaysAgo': nDaysAgo
        }

        if name in processes_instances:
            return processes_instances[name](params)

        logger.info("Processo não encontrado!") 
