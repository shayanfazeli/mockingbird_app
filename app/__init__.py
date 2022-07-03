import os
from flask import Flask, render_template
from configurations import Configurations

# - repositories
application_directory = os.path.abspath(os.path.dirname(__file__))
tweets_repo = Configurations.tweets_root
accounts_df_filepath = Configurations.accounts_df_filepath
cache_folderpath = Configurations.cache_folderpath
cache_repo = os.path.abspath(os.path.join(application_directory, '..', 'warehouse/cache'))


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
    # db.init_app(app=app)
    # migrate.init_app(app=app, db=db)
    # mail.init_app(app=app)
    from app.blueprints.main import main_blueprint
    app.register_blueprint(main_blueprint)
    from app.blueprints.topic_modeling import topic_modeling_blueprint
    app.register_blueprint(topic_modeling_blueprint)

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

    return app
