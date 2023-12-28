from flask import render_template, request, flash
from models.rankings import create_ranking


def configure_create_routes(app):
    @app.route('/create-scenario')
    def create():
        return render_template('create.html')

    @app.route('/create-scenario/end_page', methods=['GET', 'POST'])
    def create_rankings():
        name = request.form['name']
        experts = request.form['experts']
        alternatives = request.form['alternatives']
        criterions = request.form['criterions']
        start_date = request.form['selected_start_date']
        end_date = request.form['selected_end_date']
        scale = request.form['scale']
        create_ranking(name, alternatives, criterions, experts, start_date, end_date, scale)
        return render_template('end_create.html')
