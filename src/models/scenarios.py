from helpers.database import get_mysql_connection as get_db
from helpers.result import OperationResult as Result
import models.scenario_data as scenario_data


class Scenario:
    def __init__(self, model_id, in_progress=True, id=None):
        self.id = id
        self.model_id = model_id
        self.in_progress = in_progress

##### CREATE #####

def create_scenario(scenario: Scenario) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO Decision_Scenarios (model_id, in_progress) VALUES (%s, %s)', (scenario.model_id, scenario.in_progress))
    db.commit()
    scenario_id = cursor.lastrowid
    cursor.close()
    db.close()
    
    data_result = scenario_data.create_scenario_data(scenario_id)
    data_id = data_result.data['data_id']
    return Result(True, "Scenario created successfully", {"scenario_id": scenario_id, "data_id": data_id})


# def create_scenario_data(scenario_id: int) -> Result:
#     db = get_db()
#     cursor = db.cursor()
#     cursor.execute('INSERT INTO Scenario_Data (scenario_id, in_progress) VALUES (%s, %s)', (scenario_id, True))
#     data_id = cursor.lastrowid
#     db.commit()
#     cursor.close()
#     cursor = db.cursor()
#     return Result(True, "Scenario data created successfully", {"data_id": data_id})


#### GETTERS ####

def get_scenario(scenario_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Decision_Scenarios WHERE scenario_id like '%s'" % scenario_id)
    for id, model_id, in_progress in cursor:
        cursor.close()
        db.close()
        scenario = Scenario(model_id, in_progress, id)
        return Result(True, "Scenario found", {'scenario': scenario})
    return Result(False, 'Scenario is not present!')

def get_scenario_id(model_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Decision_Scenarios WHERE model_id like '%s'" % model_id)
    for scenario_id, model_id, in_progress in cursor:
        cursor.close()
        db.close()
        return Result(True, "Scenario found", {'scenario_id': scenario_id})
    return Result(False, 'Scenario is not present!')


def get_scenario_data_id(scenario_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Scenario_Data WHERE scenario_id like '%s'" % scenario_id)
    for id, scenario_id, in_progress in cursor:
        cursor.close()
        db.close()
        return Result(True, "Scenario data found", {'data_id': id})
    return Result(False, 'Scenario data is not present!')


def get_scenarios() -> list:
    scenarios = []
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Decision_Scenarios')
    for id, model_id, in_progress in cursor:
        scenarios.append(Scenario(model_id, in_progress, id))
    cursor.close()
    db.close()
    return scenarios

def get_scenarios_in_progress() -> list:
    scenarios = []
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Decision_Scenarios WHERE in_progress = 1')
    for id, model_id, in_progress in cursor:
        scenarios.append(Scenario(model_id, in_progress, id))
    cursor.close()
    db.close()
    return scenarios

def get_scenarios_completed() -> list:
    scenarios = []
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Decision_Scenarios WHERE in_progress = 0')
    for id, model_id, in_progress in cursor:
        scenarios.append(Scenario(model_id, in_progress, id))
    cursor.close()
    db.close()
    return scenarios

def get_scenario_model_id(scenario_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Decision_Scenarios WHERE scenario_id like '%s'" % scenario_id)
    for _scenario_id, model_id, in_progress in cursor:
        cursor.close()
        db.close()
        return Result(True, "Scenario found", {'model_id': model_id})
    return Result(False, 'Scenario is not present!')


##### SETTERS #####

def set_scenario_in_progress(scenario_id: int, in_progress: bool) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE Decision_Scenarios SET in_progress = %s WHERE scenario_id = %s', (in_progress, scenario_id))
    db.commit()
    cursor.close()
    db.close()
    return Result(True, "Scenario in_progress status updated successfully")

# def set_scenario_data_in_progress(scenario_id: int, in_progress: bool) -> Result:
#     db = get_db()
#     cursor = db.cursor()
#     cursor.execute('UPDATE Scenario_Data SET in_progress = %s WHERE scenario_id = %s', (in_progress, scenario_id))
#     db.commit()
#     cursor.close()
#     db.close()
#     return Result(True, "Scenario data in_progress status updated successfully")
