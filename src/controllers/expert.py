from flask import render_template, request, flash, redirect, url_for
from models.experts import Expert, get_experts, get_expert_first_name

def configure_expert_routes(app):
    @app.route('/expert/login')
    def expert_login():
        return render_template('expert_login.html', experts=get_experts())
    
    @app.route('/expert', methods=['GET', 'POST'])
    def expert():
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'login':
                return handle_login()
            
    def handle_login():
        expert_id = request.form['id']
        if not expert_id:
            flash('ID is required!')
            return redirect(url_for('expert_login'))
        
        flash("Logged in!")
        return render_template('expert.html', expert_id=expert_id, expert_name=get_expert_first_name(int(expert_id)))