from processes.ndays_ago import nDaysAgo
from processes.regular_query import RegularQuery


class ProcessFactory:
    @staticmethod
    def getInstance(name, params):
        processes_instances = {
            'regular': RegularQuery,
            'nDaysAgo': nDaysAgo
        }

        if name in processes_instances:
            return processes_instances[name](params)

        raise "Processo não encontrado!"
