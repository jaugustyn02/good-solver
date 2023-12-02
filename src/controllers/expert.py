from flask import render_template


def configure_expert_routes(app):
    @app.route('/expert')
    def expert():
        return render_template('expert.html')