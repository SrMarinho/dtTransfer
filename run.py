import argparse
import factories.mode_factory as mf
from factories.mode_factory import ModeFactory 


def init_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--params', nargs='*', default=[], type=str,
                        help='Argumentos no formato *key1 value1 *key2 value2 ...',
                        metavar='+key value', dest='params')

    args = parser.parse_args()
    
    params = {}
    if args.params:
        for i in range(0, len(args.params), 2):
            if i + 1 < len(args.params):
                params[args.params[i].lstrip('+')] = args.params[i + 1]

    if 'mode' not in params:
        params['mode'] = 'cli'

    return params

def main():
    params = init_args()
    
    mode = ModeFactory.getInstance(params['mode'], params)
    mode.run()

if __name__ == "__main__":
    main()
