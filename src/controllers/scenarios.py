from flask import render_template, request, flash, redirect, url_for
# from models.models import add_model, Model, get_model_name, get_model, add_model_alternative, delete_model_alternative, add_model_criterion, delete_model_criterion, add_model_scale, delete_model_scale, count_experts_in_model
from models.scenarios import get_scenarios_completed, get_scenarios_in_progress, get_scenario_model_id
from helpers.result import OperationResult as Result
from helpers.encoding import encode_int
from models.alternatives import Alternative
from models.criterions import Criterion
from models.scales import Scale
from datetime import datetime
import models.models as models


def configure_scenarios_routes(app):
    @app.route('/scenarios/create')
    def scenarios_create():
        if request.method == 'GET':
            return render_template('scenarios_create.html')
        
    @app.route('/scenarios/view', methods=['GET', 'POST'])
    def scenarios_view():
        if request.method == 'GET':
            scenario_id = request.args.get('scenario_id')
            model_id = get_scenario_model_id(scenario_id).data['model_id']
            model = models.get_model(model_id).data['model']
            alternatives = model.get_alternatives()
            criterias = model.get_criterias()
            scales = model.get_scales()
            survey_code = encode_int(int(model_id))
            experts_joined = models.count_experts_in_model(model_id).data['expert_count']
            surveys_completed = 0 #TODO
            return render_template('scenarios_view.html', scenario_id=scenario_id, model=model, alternatives=alternatives, criterias=criterias,
                                   scales=scales, survey_code=survey_code, experts_joined=experts_joined, surveys_completed=surveys_completed)

    @app.route('/scenarios', methods=['GET', 'POST'])
    def scenarios():
        if request.method == 'GET':
            scenarios_in_progress = get_scenarios_in_progress()
            scenarios_completed = get_scenarios_completed()
            scenarios_id = [scenario.id for scenario in scenarios_in_progress + scenarios_completed]
            scenarios_names = {scenario_id : models.get_model_name(
                    (get_scenario_model_id(scenario_id)).data['model_id']
                ).data['model_name'] for scenario_id in scenarios_id
            }
            return render_template('scenarios.html', scenarios_in_progress=scenarios_in_progress, scenarios_completed=scenarios_completed, scenarios_names=scenarios_names)
        if request.method == 'POST':
            name = request.form['name']
            ranking_method = request.form['ranking_method']
            aggregation_method = request.form['aggregation_method']
            start_date = datetime.now()
            end_date = datetime.max
            completeness_required = request.form.get('completeness_required') is not None
            result = models.add_model(models.Model(name, ranking_method, aggregation_method, completeness_required, start_date, end_date))
            if result.success:
                scenario_id = result.data['scenario_id']
                return redirect(url_for('scenarios_view', scenario_id=scenario_id))
            flash(result.message)
            return redirect(url_for('scenarios_create'))
        
    # Alternative routes    
        
    @app.route('/scenarios/alternatives', methods=['GET'])
    def scenarios_alternatives():
        if request.method == 'GET':
            scenario_id = request.args.get('scenario_id')
            model_id = get_scenario_model_id(scenario_id).data['model_id']
            model = models.get_model(model_id).data['model']
            alternatives = model.get_alternatives()
            return render_template('scenarios_alternatives.html', scenario_id=scenario_id, alternatives=alternatives)
        
    @app.route('/scenarios/add_alternative', methods=['POST'])
    def scenarios_add_alternative():
        if request.method == 'POST':
            scenario_id = request.form['scenario_id']
            model_id = get_scenario_model_id(scenario_id).data['model_id']
            new_alternative = Alternative(request.form['alternative_name'], request.form['alternative_description'])
            result = models.add_model_alternative(model_id, new_alternative)
            flash(result.message)
            return redirect(url_for('scenarios_alternatives', scenario_id=scenario_id))
        
    @app.route('/scenarios/delete_alternative', methods=['POST'])
    def scenarios_delete_alternative():
        if request.method == 'POST':
            scenario_id = request.form['scenario_id']
            model_id = get_scenario_model_id(scenario_id).data['model_id']
            alternative_id = request.form['alternative_id']
            result = models.delete_model_alternative(model_id, alternative_id)
            flash(result.message)
            return redirect(url_for('scenarios_alternatives', scenario_id=scenario_id))
        
    # Criterion routes    
        
    @app.route('/scenarios/criterias', methods=['GET'])
    def scenarios_criterias():
        if request.method == 'GET':
            scenario_id = request.args.get('scenario_id')
            model_id = get_scenario_model_id(scenario_id).data['model_id']
            model = models.get_model(model_id).data['model']
            criterias = model.get_criterias()
            return render_template('scenarios_criterias.html', scenario_id=scenario_id, criterias=criterias)    
        
    @app.route('/scenarios/add_criterion', methods=['POST'])
    def scenarios_add_criterion():
        if request.method == 'POST':
            scenario_id = request.form['scenario_id']
            model_id = get_scenario_model_id(scenario_id).data['model_id']
            new_criteria = Criterion(request.form['parent_id'], request.form['name'], request.form['description'])
            result = models.add_model_criterion(model_id, new_criteria)
            flash(result.message)
            return redirect(url_for('scenarios_criterias', scenario_id=scenario_id))
        
    @app.route('/scenarios/delete_criterion', methods=['POST'])
    def scenarios_delete_criterion():
        if request.method == 'POST':
            scenario_id = request.form['scenario_id']
            model_id = get_scenario_model_id(scenario_id).data['model_id']
            criterion_id = request.form['criterion_id']
            result = models.delete_model_criterion(model_id, criterion_id)
            flash(result.message)
            return redirect(url_for('scenarios_criterias', scenario_id=scenario_id))
        
    # Scale routes    
        
    @app.route('/scenarios/scales', methods=['GET'])
    def scenarios_scales():
        if request.method == 'GET':
            scenario_id = request.args.get('scenario_id')
            model_id = get_scenario_model_id(scenario_id).data['model_id']
            model = models.get_model(model_id).data['model']
            scales = model.get_scales()
            return render_template('scenarios_scales.html', scenario_id=scenario_id, scales=scales)
    
    @app.route('/scenarios/add_scale', methods=['POST'])
    def scenarios_add_scale():
        if request.method == 'POST':
            scenario_id = request.form['scenario_id']
            model_id = get_scenario_model_id(scenario_id).data['model_id']
            new_scale = Scale(request.form['value'], request.form['description'])
            result = models.add_model_scale(model_id, new_scale)
            flash(result.message)
            return redirect(url_for('scenarios_scales', scenario_id=scenario_id))
        
    @app.route('/scenarios/delete_scale', methods=['POST'])
    def scenarios_delete_scale():
        if request.method == 'POST':
            scenario_id = request.form['scenario_id']
            model_id = get_scenario_model_id(scenario_id).data['model_id']
            scale_id = request.form['scale_id']
            result = models.delete_model_scale(model_id, scale_id)
            flash(result.message)
            return redirect(url_for('scenarios_scales', scenario_id=scenario_id))
      
    # Options routes  
        
    @app.route('/scenarios/finalize', methods=['POST'])
    def scenarios_finalize():
        if request.method == 'POST':
            scenario_id = request.form['scenario_id']
            model_id = get_scenario_model_id(scenario_id).data['model_id']
            model = models.get_model(model_id).data['model']
            result = model.finalize()
            flash(result.message)
            return redirect(url_for('scenarios_view', scenario_id=scenario_id))
        
    @app.route('/scenarios/delete', methods=['POST'])
    def scenarios_delete():
        if request.method == 'POST':
            scenario_id = request.form['scenario_id']
            model_id = get_scenario_model_id(scenario_id).data['model_id']
            model = models.get_model(model_id).data['model']
            result = model.delete()
            flash(result.message)
            return redirect(url_for('scenarios'))