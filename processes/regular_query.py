from datetime import *
from processes.process import Process
from factories.queryable_factory import QueryableFactory
from factories.database_factory import DatabaseFactory
from factories.database_driver_factory import DatabaseDriverFactory
import processes as init


class RegularQuery(Process):
    def __init__(self, params):
        self.params = params

    def run(self):
        tableInstance = QueryableFactory.getInstance(self.params['table'], self.params)

        originalQuery = tableInstance.getQuery()

        fromCursor = fromConnection.cursor()
        fromCursor.execute(currentQuery)

        fromConnection = tableInstance.fromDriver.connection()

        numOfRows = 0

        while True:
            rows = fromCursor.fetchmany(init.ROWSNUM)
            if not rows:
                break

            numOfRows += len(rows)

            print(numOfRows, end="\r")

            tableInstance.insert(rows)

        fromCursor.close()
        fromConnection.close()
