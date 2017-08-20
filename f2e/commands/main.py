import os
import sys
import logging.config

from cliff.app import App
from cliff.commandmanager import CommandManager

from f2e import util


log = logging.getLogger(__name__)


def main(argv=sys.argv[1:]):
    myapp = F2EApp()
    return myapp.run(argv)


class F2EApp(App):

    def __init__(self):
        super(F2EApp, self).__init__(
            description='Fax to Email Gateway',
            version='0.1',
            command_manager=CommandManager('f2e.commands'),
            deferred_help=True)

    def initialize_app(self, argv):
        super(F2EApp, self).initialize_app(argv)
        if self.options.pdb:
            sys.excepthook = util.debug_hook
        if os.path.exists('.env'):
            with open('.env') as fp:
                for line in fp:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith('#'):
                        continue
                    kvdata = line.strip().split('=', 1)
                    if len(kvdata) != 2:
                        log.warning('bad .env line %r', line)
                        continue
                    key, val = kvdata
                    os.environ[key] = val

    def configure_logging(self):
        pass

    def build_option_parser(self, description, version, argparse_kwargs=None):
        parser = super(F2EApp, self).build_option_parser(
            description, version, argparse_kwargs)
        parser.add_argument('--pdb', action='store_true')
        return parser


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
