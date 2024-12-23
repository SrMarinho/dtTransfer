from processes.ndays_ago import nDaysAgo
from processes.regular_query import RegularQuery
from processes.nMonths_ago import nMonthsAgo
from config.logger.logging import logger

class ProcessFactory:
    @staticmethod
    def getInstance(name, params):
        processes_instances = {
            'regular': RegularQuery,
            'nDaysAgo': nDaysAgo,
            'nMonthsAgo': nMonthsAgo
        }

        if name in processes_instances:
            return processes_instances[name](params)

        logger.info("Processo não encontrado!") 
