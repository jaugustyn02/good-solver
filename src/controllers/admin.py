from flask import render_template, request, flash, redirect, url_for
from mysql.connector import connect
from models.experts import Expert, get_experts, create_expert, delete_expert


def configure_admin_routes(app):
    @app.route('/admin', methods=['GET', 'POST'])
    def admin():
        if request.method == 'GET':
            return render_template('admin.html', experts=get_experts())
        elif request.method == 'POST':
            action = request.form.get('action')
            
            if action == 'add_expert':
                return handle_add_expert()
            elif action == 'delete_expert':
                return handle_delete_expert()
        return render_template('admin.html', experts=get_experts())

    def handle_add_expert():
        name, mail = request.form['name'], request.form['mail']
        if not name:
            flash('Name is required!')
        elif not mail:
            flash('Mail is required!')
        else:
            expert = Expert(name, mail)
            create_expert(expert)
            flash('Expert created successfully')
                
        return redirect(url_for('admin'))
    
    def handle_delete_expert():
        expert_id = request.form['id']
        print('EXPERT ID:', expert_id)
        if not id:
            flash('ID is required!')
        else:
            delete_expert(int(expert_id))
            flash('Expert deleted successfully')
            
        return redirect(url_for('admin'))