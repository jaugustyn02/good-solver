from flask import render_template, request, flash
from mysql.connector import connect
from models.experts import get_experts, create_expert, Expert


def configure_admin_routes(app):
    # create expert
    @app.route('/admin', methods=['GET', 'POST'])
    def admin():
        if request.method == 'POST':
            name, mail = request.form['name'], request.form['mail']
            if not name:
                flash('Name is required')
            elif not mail:
                flash('Mail is required')
            else:
                expert = Expert(name, mail)
                create_expert(expert)
                flash('Expert created successfully')
                
        return render_template('admin.html', experts=get_experts())