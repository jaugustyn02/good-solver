from flask import render_template


def configure_create_routes(app):
    @app.route('/create-ranking')
    def create():
        return render_template('create.html')