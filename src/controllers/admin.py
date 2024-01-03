from flask import render_template, request, flash, redirect, url_for
from mysql.connector import connect
from models.experts import Expert, get_experts, create_expert, delete_expert
from models.alternatives import Alternative, get_alternatives, create_alternative, delete_alternative


def configure_admin_routes(app):
    @app.route('/admin', methods=['GET', 'POST'])
    def admin():
        if request.method == 'GET':
            return render_template('admin.html', experts=get_experts(), alternatives=get_alternatives())
        elif request.method == 'POST':
            action = request.form.get('action')
            
            if action == 'add_expert':
                return handle_add_expert()
            elif action == 'delete_expert':
                return handle_delete_expert()
            elif action == 'add_alternative':
                return handle_add_alternative()
            elif action == 'delete_alternative':
                return handle_delete_alternative()
        return render_template('admin.html', experts=get_experts(), alternatives=get_alternatives())

    def handle_add_expert():
        name, mail = request.form['name'], request.form['mail']
        if not name:
            flash('Name is required!')
        elif not mail:
            flash('Mail is required!')
        else:
            expert = Expert(name, mail)
            result = create_expert(expert)
            flash(result.message)
        return redirect(url_for('admin'))
    
    def handle_delete_expert():
        expert_id = request.form['id']
        if not expert_id:
            flash('ID is required!')
        else:
            result = delete_expert(int(expert_id))
            flash(result.message)
        return redirect(url_for('admin'))
    
    def handle_add_alternative():
        name, description = request.form['name'], request.form['description']
        if not name:
            flash('Name is required!')
        else:
            alternative = Alternative(name, description) if description != "" else Alternative(name)
            result = create_alternative(alternative)
            flash(result.message)
        return redirect(url_for('admin'))
    
    def handle_delete_alternative():
        alternative_id = request.form['id']
        if not alternative_id:
            flash('ID is required!')
        else:
            result = delete_alternative(int(alternative_id))
            flash(result.message)
        return redirect(url_for('admin'))