from flask import render_template


def configure_rankings_routes(app):
    @app.route('/rankings')
    def rankings():
        return render_template('rankings.html')