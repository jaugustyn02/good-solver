from flask import render_template, request, flash, redirect, url_for
from models.experts import Expert, get_experts, get_expert_first_name
from models.scenarios import Scenario, get_scenarios_in_progress, get_scenarios_completed

def configure_expert_routes(app):
    @app.route('/expert/login')
    def expert_login():
        return render_template('expert_login.html', experts=get_experts())
    
    @app.route('/expert', methods=['GET', 'POST'])
    def expert():
        if request.method == 'GET':
            expert_id = request.args.get('id')
            if expert_id:
                return handle_expert_page(int(expert_id))
            else:
                return redirect(url_for('expert_login'))
            
            
    def handle_expert_page(expert_id: int):
        expert_name = get_expert_first_name(expert_id)
        scenarios_in_progress = get_scenarios_in_progress()
        scenarios_ended = get_scenarios_completed()
        
        return render_template('expert.html', expert_id=expert_id, expert_name=expert_name, scenarios_in_progress=scenarios_in_progress, scenarios_ended=scenarios_ended)
