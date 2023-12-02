from flask import render_template


def configure_index_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')