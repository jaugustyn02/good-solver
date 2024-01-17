from flask import render_template, request, flash, redirect, url_for
from helpers.encoding import encode_int
from models.alternatives import Alternative, get_alternative
from models.data_matrices import find_empty_matrix_field, get_data_matrix, complete_all_other_fields
from models.scenario_data import get_scenario_data
from models.criterions import Criterion, get_criteria
from models.scales import Scale
from models.matrix_element import MatrixElement, create_matrix_element
from datetime import datetime
import models.models as models
import models.scenarios as Scenarios
from models.scenario_weights import get_final_scenario_weights


def configure_scenarios_routes(app):
    @app.route('/scenarios/create')
    def scenarios_create():
        if request.method == 'GET':
            return render_template('scenarios_create.html')
        
    @app.route('/scenarios/delete/confirm', methods=['GET', 'POST'])
    def scenarios_delete_confirm():
        if request.method == 'POST':
            scenario_id = request.args.get('scenario_id')
            result = Scenarios.delete_scenario(scenario_id)
            flash(result.message)
            return redirect(url_for('scenarios'))
        else:
            scenario_id = request.args.get('scenario_id')
            return render_template('scenarios_delete_confirm.html', scenario_id=scenario_id)

    @app.route('/scenarios/complete', methods=['GET', 'POST'])
    def scenarios_complete():
        if request.method == 'POST':
            model_id = request.args.get('model_id')
            expert_id = request.args.get('expert_id')
            expert_name = request.args.get('expert_name')
            scenario_id = request.args.get('scenario_id')
            model = models.get_model(model_id).data['model']
            scales = model.get_scales()

            slider_value = int(request.form['rangeSlider'])
            criterion_id = request.args.get('criterion_id')
            alt1_id = request.args.get('alternative1_id')
            alt2_id = request.args.get('alternative2_id')
            data = get_scenario_data(scenario_id)
            data_id = data.data['data'].id
            data_matrix = get_data_matrix(data_id, expert_id, criterion_id).data['data']
            
            # slider_value is from range 1-scales_length to scales_length-1, it represents the index of the scale and which alternative is better
            scale_value = scales[abs(int(slider_value))].value
            if slider_value < 0:
                create_matrix_element(MatrixElement(data_matrix.id,alt1_id,alt2_id, float(scale_value)))
                create_matrix_element(MatrixElement(data_matrix.id,alt2_id,alt1_id,1 / float(scale_value)))
            else:
                create_matrix_element(MatrixElement(data_matrix.id,alt1_id,alt2_id,1 / float(scale_value)))
                create_matrix_element(MatrixElement(data_matrix.id,alt2_id,alt1_id,float(scale_value)))
                
            res = find_empty_matrix_field(expert_id, scenario_id, model.get_criterias(), model.get_alternatives())
            if res.success:
                alt1_id, alt2_id, criterion = res.data['data']
                alt1 = get_alternative(alt1_id)
                alt2 = get_alternative(alt2_id)
                if alt1.success:
                    alt1 = alt1.data['alternative']
                    alt2 = alt2.data['alternative']
                else:
                    alt1 = get_criteria(alt1_id).data['criterion']
                    alt2 = get_criteria(alt2_id).data['criterion']
                return render_template('scenarios_complete.html', scenario_id=scenario_id, expert_id=expert_id,
                                       model_id=model_id, scales=scales, expert_name=expert_name, model=model,
                                       alt1=alt1, alt2=alt2, criterion=criterion)
            else:
                complete_all_other_fields(expert_id, scenario_id, model.get_criterias(), model.get_alternatives())
                flash("Thank you for filling out the survey")
                return redirect(url_for('scenarios'))
        else:
            model_id = request.args.get('model_id')
            expert_id = request.args.get('expert_id')
            expert_name = request.args.get('expert_name')
            scenario_id = Scenarios.get_scenario_id(model_id).data['scenario_id']
            model = models.get_model(model_id).data['model']
            scales = model.get_scales()
            res = find_empty_matrix_field(expert_id, scenario_id, model.get_criterias(), model.get_alternatives())
            if res.success:
                alt1_id, alt2_id, criterion = res.data['data']
                alt1 = get_alternative(alt1_id)
                alt2 = get_alternative(alt2_id)
                if alt1.success:
                    alt1 = alt1.data['alternative']
                    alt2 = alt2.data['alternative']
                else:
                    alt1 = get_criteria(alt1_id).data['criterion']
                    alt2 = get_criteria(alt2_id).data['criterion']
                return render_template('scenarios_complete.html', scenario_id=scenario_id, expert_id=expert_id,
                                       model_id=model_id, scales=scales, expert_name=expert_name, model=model,
                                       alt1=alt1, alt2=alt2, criterion=criterion)
            else:
                flash("Thank you for filling out the survey")
                return redirect(url_for('scenarios'))
        
    @app.route('/scenarios/view', methods=['GET', 'POST'])
    def scenarios_view():
        if request.method == 'GET':
            scenario_id = request.args.get('scenario_id')
            model_id = Scenarios.get_scenario_model_id(scenario_id).data['model_id']
            model = models.get_model(model_id).data['model']
            alternatives = model.get_alternatives()
            criterias = model.get_criterias()
            scales = model.get_scales()
            survey_code = encode_int(int(model_id))
            experts_joined = models.count_experts_in_model(model_id).data['expert_count']
            surveys_completed = models.surveys_completed_count(model_id)
            confirmed = get_scenario_data(scenario_id).data['data'].in_progress
            finalized = Scenarios.get_scenario(scenario_id).data['scenario'].in_progress
            return render_template('scenarios_view.html', scenario_id=scenario_id, model=model, finalized=finalized,
                                   alternatives=alternatives, criterias=criterias,scales=scales, survey_code=survey_code,
                                   experts_joined=experts_joined, surveys_completed=surveys_completed, confirmed=confirmed)

    @app.route('/scenarios', methods=['GET', 'POST'])
    def scenarios():
        if request.method == 'GET':
            scenarios_in_progress = Scenarios.get_scenarios_in_progress()
            scenarios_completed = Scenarios.get_scenarios_completed()
            scenarios_id = [scenario.id for scenario in scenarios_in_progress + scenarios_completed]
            scenarios_names = {scenario_id : models.get_model_name(
                    (Scenarios.get_scenario_model_id(scenario_id)).data['model_id']
                ).data['model_name'] for scenario_id in scenarios_id
            }
            return render_template('scenarios.html', scenarios_in_progress=scenarios_in_progress, scenarios_completed=scenarios_completed, scenarios_names=scenarios_names)
        if request.method == 'POST':
            name = request.form['name']
            ranking_method = request.form['ranking_method']
            aggregation_method = request.form['aggregation_method']
            start_date = datetime.now()
            end_date = request.form['end_date']
            if end_date == "":
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
            model_id = Scenarios.get_scenario_model_id(scenario_id).data['model_id']
            model = models.get_model(model_id).data['model']
            alternatives = model.get_alternatives()
            expert_count = models.count_experts_in_model(model_id)
            if expert_count.success and expert_count.data['expert_count'] > 0:
                flash("The survey has started, the scenario can't be edited")
                return redirect(url_for('scenarios'))
            return render_template('scenarios_alternatives.html', scenario_id=scenario_id, alternatives=alternatives)
        
    @app.route('/scenarios/add_alternative', methods=['POST'])
    def scenarios_add_alternative():
        if request.method == 'POST':
            scenario_id = request.form['scenario_id']
            model_id = Scenarios.get_scenario_model_id(scenario_id).data['model_id']
            new_alternative = Alternative(request.form['alternative_name'], request.form['alternative_description'])
            result = models.add_model_alternative(model_id, new_alternative)
            flash(result.message)
            return redirect(url_for('scenarios_alternatives', scenario_id=scenario_id))
        
    @app.route('/scenarios/delete_alternative', methods=['POST'])
    def scenarios_delete_alternative():
        if request.method == 'POST':
            scenario_id = request.form['scenario_id']
            model_id = Scenarios.get_scenario_model_id(scenario_id).data['model_id']
            alternative_id = request.form['alternative_id']
            result = models.delete_model_alternative(model_id, alternative_id)
            flash(result.message)
            return redirect(url_for('scenarios_alternatives', scenario_id=scenario_id))
        
    # Criterion routes    
        
    @app.route('/scenarios/criterias', methods=['GET'])
    def scenarios_criterias():
        if request.method == 'GET':
            scenario_id = request.args.get('scenario_id')
            model_id = Scenarios.get_scenario_model_id(scenario_id).data['model_id']
            model = models.get_model(model_id).data['model']
            criterias = model.get_criterias()
            expert_count = models.count_experts_in_model(model_id)
            if expert_count.success and expert_count.data['expert_count'] > 0:
                flash("The survey has started, the scenario can't be edited")
                return redirect(url_for('scenarios'))
            return render_template('scenarios_criterias.html', scenario_id=scenario_id, criterias=criterias)    
        
    @app.route('/scenarios/add_criterion', methods=['POST'])
    def scenarios_add_criterion():
        if request.method == 'POST':
            scenario_id = request.form['scenario_id']
            model_id = Scenarios.get_scenario_model_id(scenario_id).data['model_id']
            new_criteria = Criterion(request.form['parent_id'], request.form['name'], request.form['description'])
            result = models.add_model_criterion(model_id, new_criteria)
            flash(result.message)
            return redirect(url_for('scenarios_criterias', scenario_id=scenario_id))
        
    @app.route('/scenarios/delete_criterion', methods=['POST'])
    def scenarios_delete_criterion():
        if request.method == 'POST':
            scenario_id = request.form['scenario_id']
            model_id = Scenarios.get_scenario_model_id(scenario_id).data['model_id']
            criterion_id = request.form['criterion_id']
            result = models.delete_model_criterion(model_id, criterion_id)
            flash(result.message)
            return redirect(url_for('scenarios_criterias', scenario_id=scenario_id))
        
    # Scale routes    
        
    @app.route('/scenarios/scales', methods=['GET'])
    def scenarios_scales():
        if request.method == 'GET':
            scenario_id = request.args.get('scenario_id')
            model_id = Scenarios.get_scenario_model_id(scenario_id).data['model_id']
            model = models.get_model(model_id).data['model']
            scales = model.get_scales()
            expert_count = models.count_experts_in_model(model_id)
            if expert_count.success and expert_count.data['expert_count'] > 0:
                flash("The survey has started, the scenario can't be edited")
                return redirect(url_for('scenarios'))
            return render_template('scenarios_scales.html', scenario_id=scenario_id, scales=scales)
    
    @app.route('/scenarios/add_scale', methods=['POST'])
    def scenarios_add_scale():
        if request.method == 'POST':
            scenario_id = request.form['scenario_id']
            model_id = Scenarios.get_scenario_model_id(scenario_id).data['model_id']
            new_scale = Scale(request.form['value'], request.form['description'])
            result = models.add_model_scale(model_id, new_scale)
            flash(result.message)
            return redirect(url_for('scenarios_scales', scenario_id=scenario_id))
        
    @app.route('/scenarios/delete_scale', methods=['POST'])
    def scenarios_delete_scale():
        if request.method == 'POST':
            scenario_id = request.form['scenario_id']
            model_id = Scenarios.get_scenario_model_id(scenario_id).data['model_id']
            scale_id = request.form['scale_id']
            result = models.delete_model_scale(model_id, scale_id)
            flash(result.message)
            return redirect(url_for('scenarios_scales', scenario_id=scenario_id))
      
    # Options routes  
    
    @app.route('/scenarios/confirm', methods=['POST'])
    def scenarios_confirm():
        if request.method == 'POST':
            scenario_id = request.form['scenario_id']
            model_id = Scenarios.get_scenario_model_id(scenario_id).data['model_id']
            model = models.get_model(model_id).data['model']
            result = model.confirm()
            flash(result.message)
            return redirect(url_for('scenarios_view', scenario_id=scenario_id))
        
        
    @app.route('/scenarios/finalize', methods=['POST'])
    def scenarios_finalize():
        if request.method == 'POST':
            scenario_id = request.form['scenario_id']
            model_id = Scenarios.get_scenario_model_id(scenario_id).data['model_id']
            model = models.get_model(model_id).data['model']
            result = model.finalize()
            flash(result.message)
            return redirect(url_for('scenarios_view', scenario_id=scenario_id))

    @app.route('/ranking/show', methods=['GET', 'POST'])
    def ranking_show():
        if request.method == 'POST':
            ranking_name = request.form['name']
            scenario_id = request.form['scenario_id']
            if scenario_id == "":
                model_id = request.form['scenario_id']
                scenario_id = Scenarios.get_scenario_id(model_id).data['scenario_id']
            ranking_ = get_final_scenario_weights(scenario_id).data['values']
            ranking = sorted(ranking_, key=lambda x: -x[1])
            ranking_data = []
            for i in ranking_:
                ranking_data.append(i[1])
            return render_template('show_rankings.html', ranking_name=ranking_name, ranking=ranking, ranking_data=ranking_data)
        if request.method == 'GET':
            ranking_name = request.args.get('name')
            scenario_id = ""
            if scenario_id == "":
                model_id = request.args.get('model_id')
                scenario_id = Scenarios.get_scenario_id(model_id).data['scenario_id']
            ranking_ = get_final_scenario_weights(scenario_id).data['values']
            ranking = sorted(ranking_, key=lambda x: -x[1])
            ranking_data = []
            for i in ranking_:
                ranking_data.append(i[1])
            return render_template('show_rankings.html', ranking_name=ranking_name, ranking=ranking, ranking_data=ranking_data)

