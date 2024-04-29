from config.modes.mode import Mode
from factories.process_factory import ProcessFactory

class Cli(Mode):
    def __init__(self, params):
        self.params = params

    def run(self):
        process = ProcessFactory.getInstance(self.params['process'], self.params)
        process.run()
