import os
from app import create_app, application_directory, scheduler, mail
from flask import send_from_directory

application = create_app()
from app.libraries.scheduling.queue_processing import word_cloud_request_processor, \
    word_frequency_request_processor, \
    topic_modeling_request_processor
# from flask_mail import Message
from flask_apscheduler import APScheduler
scheduler.start()


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
    application.run(port=5000, debug=True, host='0.0.0.0')
