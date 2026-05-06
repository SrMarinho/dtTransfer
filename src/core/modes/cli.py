from src.core.modes.mode import Mode
from src.factories.process_factory import ProcessFactory

class Cli(Mode):
    def __init__(self, params):
        self.params = params

    def run(self):
        process = ProcessFactory.getInstance(self.params['process'], self.params)
        process.run()
