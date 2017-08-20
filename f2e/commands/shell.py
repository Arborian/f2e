"""Shell command."""
import logging

from cliff.command import Command
from IPython import embed

from f2e.app import make_app

log = logging.getLogger(__name__)


class Shell(Command):
    """Run an interactive shell."""

    def take_action(self, parsed_args):
        app = make_app(
            SERVER_NAME='shell',
            EVENTLET=False)
        with app.app_context():
            embed()
