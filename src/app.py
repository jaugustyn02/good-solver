from flask import Flask, render_template, request
from mysql.connector import connect
from config import app_config
from controllers import index, admin, expert, rankings, scenarios


app = Flask(__name__)
app.config.from_object(app_config)


index.configure_index_routes(app)
admin.configure_admin_routes(app)
scenarios.configure_scenarios_routes(app)
expert.configure_expert_routes(app)
rankings.configure_rankings_routes(app)

if __name__ == '__main__':
    app.run()
