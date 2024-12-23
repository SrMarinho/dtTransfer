from processes import Process
from factories.queryable_factory import QueryableFactory
from factories.database_factory import DatabaseFactory
from factories.database_driver_factory import DatabaseDriverFactory

class PerUnit(Process):
    @staticmethod
    def run(table):
        table = QueryableFactory.getInstance(table)
        fromDriver = DatabaseDriverFactory(table.fromDatabaseDriver)
        query = table.getQuery()

        
