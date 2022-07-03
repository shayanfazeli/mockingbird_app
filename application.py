from typing import Dict
import os
from app import create_app, application_directory
from flask import redirect, send_from_directory
application = create_app()


@application.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(application_directory, 'static'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@application.shell_context_processor
def make_shell_context():
    """
    The :func:`make_shell_context` build the flask shell context given the current entities.
    It can be called by running `flask shell` in the application root directory.
    Returns
    ----------
    The output of this method is a `Dict` type including the entities and methods to be used in shell
    """
    return {}


if __name__ == "__main__":
    application.run()
