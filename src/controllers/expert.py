from flask import render_template, request, flash, redirect, url_for
from models.experts import Expert, get_experts, get_expert_first_name, get_expert_models_ended, get_expert_models_in_progress, create_expert
from models.models import get_model, add_expert_to_model
from helpers.encoding import decode_int

def configure_expert_routes(app):
    @app.route('/expert/login')
    def expert_login():
        return render_template('expert_login.html', experts=get_experts())
    
    @app.route('/expert/signup', methods=['POST'])
    def expert_singup():
        if request.method == 'POST':
            name = request.form['name']
            mail = request.form['email']
            result = create_expert(Expert(name, mail))
            if result.success:
                expert_id = result.data['expert_id']
                return redirect(url_for('expert', expert_id=expert_id))
            flash(result.message)
            return redirect(url_for('expert_login'))
    
    @app.route('/expert', methods=['GET', 'POST'])
    def expert():
        if request.method == 'GET':
            expert_id = request.args.get('expert_id')
            if expert_id:
                return handle_expert_page(int(expert_id))
            else:
                return redirect(url_for('expert_login'))
            
    @app.route('/expert/join', methods=['POST'])
    def expert_join():
        if request.method == 'POST':
            expert_id = request.form['expert_id']
            access_code = request.form['access_code']
            if not access_code.isdigit():
                flash('Access code must be a number')
                return redirect(url_for('expert', expert_id=expert_id))
            result = get_model(decode_int(access_code))
            if not result.success:
                flash('Invalid access code')
                return redirect(url_for('expert', expert_id=expert_id))
            model = result.data['model']
            result = add_expert_to_model(model.id, expert_id)
            flash(result.message)
            if not result.success:
                return redirect(url_for('expert', expert_id=expert_id))
            return redirect(url_for('expert', expert_id=expert_id))
            
    def handle_expert_page(expert_id: int):
        expert_name = get_expert_first_name(expert_id)
        surveys_ongoing = get_expert_models_in_progress(expert_id)
        surveys_ended = get_expert_models_ended(expert_id)
        return render_template('expert.html', expert_id=expert_id, expert_name=expert_name, surveys_ongoing=surveys_ongoing, surveys_ended=surveys_ended)

    