from helpers.database import get_mysql_connection as get_db
from helpers.result import OperationResult as Result


class Scenario:
    def __init__(self, model_id, in_progress, id=None):
        self.id = id
        self.model_id = model_id
        self.in_progress = in_progress


def get_scenario_id(model_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Decision_Scenarios WHERE model_id like '%s'" % model_id)
    if cursor.fetchone() is None:
        return Result(False, 'Scenario is not present!')
    print("brrr")
    print(model_id)
    print(cursor)
    print(cursor.fetchone())
    print(cursor.fetchall())
    for scenario_id, model_id, in_progress in cursor:
        print(scenario_id)
        print("bzz")
        cursor.close()
        db.close()
        print(scenario_id)
        return scenario_id


def get_data_id(scenario_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Scenario_Data WHERE scenario_id like '%s'" % scenario_id)
    if cursor.fetchone() is None:
        return Result(False, 'Scenario data is not present!')
    for id, scenario_id, in_progress in cursor:
        cursor.close()
        db.close()
        return id


def create_scenario(scenario: Scenario) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO Decision_Scenarios (model_id, in_progress) VALUES (%s, %s)', (scenario.model_id, scenario.in_progress))
    db.commit()
    cursor.close()
    db.close()
    return Result(True, "Scenario created successfully")


def create_scenario_data(model_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Decision_Scenarios WHERE model_id like '%s'" % model_id)
    scenario_id_ = 1
    in_progress_ = None
    for scenario_id, model_id, in_progress in cursor:
        scenario_id_ = scenario_id
        in_progress_ = in_progress
    cursor.close()
    cursor = db.cursor()
    cursor.execute('INSERT INTO Scenario_Data (scenario_id, in_progress) VALUES (%s, %s)', (scenario_id_, in_progress_))
    db.commit()
    cursor.close()
    cursor = db.cursor()
    cursor.execute("SELECT data_id FROM Scenario_Data WHERE scenario_id like '%s'" % scenario_id_)
    for data_id in cursor:
        db.close()
        return data_id
    return Result(True, "Scenario data created successfully")
