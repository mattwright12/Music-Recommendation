import os

from flask import Flask


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        # store the database in the instance folder
        DATABASE=os.path.join(app.instance_path, "recommend.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register the database commands
    from recommend import db

    db.init_app(app)

    # apply the blueprints to the app
    from recommend import auth, add_tastes, landing_page, my_playlists, generate_playlists, my_profile, change_password

    app.register_blueprint(auth.bp)
    app.register_blueprint(add_tastes.bp)
    app.register_blueprint(landing_page.bp)
    app.register_blueprint(my_playlists.bp)
    app.register_blueprint(generate_playlists.bp)
    app.register_blueprint(my_profile.bp)
    app.register_blueprint(change_password.bp)

    # make url_for('index') == url_for('blog.index')
    # in another app, you might define a separate main index here with
    # app.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    app.add_url_rule("/login", endpoint="login")
    app.add_url_rule("/add_tastes", endpoint="add_tastes")
    app.add_url_rule("/my_playlists", endpoint='my_playlists')
    app.add_url_rule("/add_tastes/generate_playlists", endpoint="generate_playlists")
    app.add_url_rule("/add_tastes/my_profile", endpoint="my_profile")
    app.add_url_rule("/add_tastes/change_password", endpoint="change_password")

    return app
