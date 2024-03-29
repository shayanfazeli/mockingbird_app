import os
from flask import render_template, Flask
from flask_mail import Mail
from configurations import Configurations
from flask_apscheduler import APScheduler
scheduler = APScheduler()
mail = Mail()

# - repositories
application_directory = os.path.abspath(os.path.dirname(__file__))
tweets_repo = Configurations.tweets_root
accounts_df_filepath = Configurations.accounts_df_filepath
cache_folderpath = Configurations.cache_folderpath
os.makedirs(os.path.join(cache_folderpath, 'trajectory'), exist_ok=True)
os.makedirs(os.path.join(cache_folderpath, 'word_clouds'), exist_ok=True)
os.makedirs(os.path.join(cache_folderpath, 'word_frequencies'), exist_ok=True)
os.makedirs(os.path.join(cache_folderpath, 'lda_visualization'), exist_ok=True)
os.makedirs(os.path.join(cache_folderpath, 'text_and_token'), exist_ok=True)
os.makedirs(os.path.join(cache_folderpath, 'trends'), exist_ok=True)
os.makedirs(os.path.join(cache_folderpath, 'topic_model'), exist_ok=True)
os.makedirs(os.path.join(cache_folderpath, 'requests'), exist_ok=True)
os.makedirs(os.path.join(cache_folderpath, 'requests/args'), exist_ok=True)
os.makedirs(os.path.join(cache_folderpath, 'requests/emails'), exist_ok=True)


def create_app(configuration_class: object = Configurations):
    """
    The :func:`create_app` is the most important method in this library. It starts
    by creating the application, preparing the context, initiating the security measures, etc.
    Parameters
    ----------
    configuration_class: `object`, optional (default=Configurations)
        The configuration is set in this method using an object, and the parameters are defined
        in the configuration object stored in `configurations.py`, which is the default value as well.
    Returns
    ----------
    This method returns the application context and the user datastore object
    """
    app = Flask(__name__)
    app.config.from_object(configuration_class)
    from app.blueprints.main import main_blueprint
    app.register_blueprint(main_blueprint)
    from app.blueprints.topic_modeling import topic_modeling_blueprint
    app.register_blueprint(topic_modeling_blueprint)
    from app.blueprints.word_frequency import word_frequencies_blueprint
    app.register_blueprint(word_frequencies_blueprint)
    from app.blueprints.word_cloud import word_clouds_blueprint
    app.register_blueprint(word_clouds_blueprint)
    from app.blueprints.email_notification import email_notification_blueprint
    app.register_blueprint(email_notification_blueprint)

    @app.errorhandler(404)
    def error_404(e):
        # note that we set the 404 status explicitly
        return render_template('errors/error.html', error_code=404, error_message="Requested Page Was Not Found"), 404

    @app.errorhandler(500)
    def error_500(e):
        # note that we set the 404 status explicitly
        return render_template('errors/error.html', error_code=500,
                               error_message="Please Check Your Parameters and Try Again"), 500

    @app.errorhandler(502)
    def error_502(e):
        # note that we set the 404 status explicitly
        return render_template('errors/error.html', error_code=502,
                               error_message="Request Timeout"), 502

    @app.errorhandler(504)
    def error_504(e):
        # note that we set the 404 status explicitly
        return render_template('errors/error.html', error_code=500,
                               error_message="Request Timeout"), 504

    scheduler.init_app(app)
    mail.init_app(app)
    return app
