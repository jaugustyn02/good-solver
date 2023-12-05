from flask import render_template, request
from helpers.database import get_mysql_connection as get_db
from models.rankings import all_rankings, get_ranking


def configure_rankings_routes(app):
    @app.route('/rankings')
    def rankings():
        return render_template('rankings.html', arguments=all_rankings())

    @app.route('/rankings/show', methods=['GET', 'POST'])
    def show_rankings():
        ranking_name = request.form['sel']
        ranking = get_ranking(ranking_name)
        return render_template('show_rankings.html', ranking_name=ranking_name, ranking=ranking)
