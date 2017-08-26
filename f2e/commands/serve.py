"""Shell command."""
import os
import logging

from cliff.command import Command

from f2e.app import make_app

log = logging.getLogger(__name__)


class Serve(Command):
    """Run locally."""

    def get_parser(self, prog_name):
        parser = super(Serve, self).get_parser(prog_name)
        parser.add_argument(
            '--debug-server', action='store_true',
            help='Use debug mode')
        return parser

    def take_action(self, parsed_args):
        app = make_app()
        port = int(os.environ.get("PORT", 5000))
        host = os.environ.get("HOST", '127.0.0.1')
        app.run(
            host=host, port=port,
            threaded=not parsed_args.debug_server,
            debug=parsed_args.debug_server,
            use_reloader=parsed_args.debug_server)
