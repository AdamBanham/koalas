"""
Command line tool to quickly create an XES log from arguments.
"""


import argparse

from pmkoalas import dtlog, export


def traces_to_xes(traces,log_fname):
    log = dtlog.convert( *traces) 
    export.export_to_xes_simple( log_fname, log )
    print(f'Wrote {len(traces)} traces to {log_fname}')


DESCRIPTION = \
"""
Output delimited input traces to an XES log.

Delimited traces are defined by the koalas.dtlog module.
"""

EPILOG = \
"""
Example use:

%(prog)s \"a b c\" \"a d c\" -f choice.xes
"""


def main():
    parser = argparse.ArgumentParser( description=DESCRIPTION, epilog=EPILOG)
    parser.add_argument('-f','--file',default='out.xes', 
                        help="Name of the output XES file" )
    parser.add_argument('traces', nargs='+')
    args = parser.parse_args()
    traces_to_xes( args.traces, args.file )

if __name__ == '__main__':
    main()

