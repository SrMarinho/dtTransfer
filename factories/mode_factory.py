from config.modes.cli import Cli

class ModeFactory:
    def getInstance(mode, params):
        modes = {
            'cli': Cli
        }
        if mode in modes:
            return modes[mode](params)
        else:
            return Cli(params)

