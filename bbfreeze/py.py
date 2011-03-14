#! /usr/bin/env python
"""interactive python prompt with tab completion"""

# code inspired by matplotlib
# (http://matplotlib.sourceforge.net/examples/interactive.py)

from code import InteractiveConsole
from code import compile_command
import time
try:
    # rlcompleter also depends on readline
    import rlcompleter
    import readline
except ImportError:
    readline = None


class MyConsole(InteractiveConsole):
    needed = 0.0

    def __init__(self, *args, **kwargs):
        InteractiveConsole.__init__(self, *args, **kwargs)

        if not readline:
            return

        try:  # this form only works with python 2.3
            self.completer = rlcompleter.Completer(self.locals)
        except:  # simpler for py2.2
            self.completer = rlcompleter.Completer()

        readline.set_completer(self.completer.complete)
        # Use tab for completions
        readline.parse_and_bind('tab: complete')
        # This forces readline to automatically print the above list when tab
        # completion is set to 'complete'.
        readline.parse_and_bind('set show-all-if-ambiguous on')
        # Bindings for incremental searches in the history. These searches
        # use the string typed so far on the command line and search
        # anything in the previous input history containing them.
        readline.parse_and_bind('"\C-r": reverse-search-history')
        readline.parse_and_bind('"\C-s": forward-search-history')

    def runcode(self, code):
        stime = time.time()
        try:
            return InteractiveConsole.runcode(self, code)
        finally:
            self.needed = time.time() - stime

    def raw_input(self, prompt=""):
        if self.needed > 0.01:
            prompt = "[%.2fs]\n%s" % (self.needed, prompt)
            self.needed = 0.0

        return InteractiveConsole.raw_input(self, prompt)


if __name__ == '__main__':
    if readline:
        import os
        histfile = os.path.expanduser("~/.pyhistory")
        if os.path.exists(histfile):
            readline.read_history_file(histfile)

    # Emulate necessary python options for pytest_xdist to work with
    # bundled python interpreter.
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-u', dest='cache_stdin_out', action='store_true',
            help='Emulate python interpreter option -u. It is ignored.')
    parser.add_option('-c', dest='command', action='store', default=None,
            help='Specify the command to execute.')
    (options, args) = parser.parse_args()

    import sys
    sys.argv = [sys.argv[0]] + args

    try:
        # Execute python command (code) if given
        if options.command:
            compiled_code = compile_command(options.command, '<string>')
            MyConsole(locals=dict()).runcode(compiled_code)
        else:
            MyConsole(locals=dict()).interact()
    finally:
        if readline:
            readline.write_history_file(histfile)
