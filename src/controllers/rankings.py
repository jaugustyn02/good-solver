import json

from flask import render_template, request, jsonify
from models.scenarios import get_scenarios_completed, get_scenario_model_id, get_scenario_id
from models.models import get_model, get_model_name, get_model_data
from models.scenario_weights import get_final_scenario_weights


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
        if request.method == 'GET':
            model_id = request.args.get('model_id')
        else:
            model_id = request.form['model_id']
        ranking_name = get_model_name(model_id).data['model_name']
        scenario_id = get_scenario_id(model_id).data['scenario_id']
        ranking_ = get_final_scenario_weights(scenario_id).data['values']
        ranking = sorted(ranking_, key=lambda x: -x[1])
        ranking_data = []
        for i in ranking_:
            ranking_data.append(i[1])
        return render_template('show_rankings.html', ranking_name=ranking_name, ranking=ranking, ranking_data=[ranking_data])

    @app.route('/export_json', methods=['GET', 'POST'])
    def export_json():
        ranking_name = request.args.get('ranking_name')
        ranking_data = request.args.get('ranking_data')
        data = get_model_data(ranking_name, ranking_data)
        return json.dumps(data, indent=4)
