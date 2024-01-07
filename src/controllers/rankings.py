from flask import render_template, request
from helpers.database import get_mysql_connection as get_db
from models.scenarios import get_scenarios_completed, get_scenario_model_id, get_scenario_id
from models.models import get_model, get_model_id
from models.scenario_weights import get_scenario_weights, get_scenario_weights_id
from models.weights_vector_element import get_vector_elements_values


def configure_rankings_routes(app):
    @app.route('/rankings')
    def rankings():
        scenarios = get_scenarios_completed()
        models = []
        for scenario in scenarios:
            model_id = get_scenario_model_id(scenario.id)
            if model_id.success:
                model_id = model_id.data['model_id']
                model = get_model(model_id)
                if model.success:
                    models.append(model.data['model'])

        return render_template('rankings.html', arguments=models)

    @app.route('/rankings/show', methods=['GET', 'POST'])
    def show_rankings():
        ranking_name = request.form['sel']
        model_id = get_model_id(ranking_name).data['model_id']
        scenario_id = get_scenario_id(model_id).data['scenario_id']
        # ranking = get_scenario_weights(scenario_id)
        weights_id = get_scenario_weights_id(scenario_id)
        ranking = get_vector_elements_values(weights_id)
        return render_template('show_rankings.html', ranking_name=ranking_name, ranking=ranking)
