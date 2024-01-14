from helpers.database import get_mysql_connection as get_db
from helpers.result import OperationResult as Result
from models.weights_vector_element import get_vector_elements_values, delete_element


class ScenarioWeights:
    def __init__(self, scenario_id, criterion_id, size, in_progress, id=None):
        self.id = id
        self.scenario_id = scenario_id
        self.criterion_id = criterion_id
        self.size = size
        self.in_progress = in_progress


def create_scenario_weights(scenario_weights: ScenarioWeights) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO Scenario_Weights (scenario_id, criterion_id, size, in_progress) VALUES (%s, %s, %s, %s)',
                   (scenario_weights.scenario_id, scenario_weights.criterion_id, scenario_weights.size, scenario_weights.in_progress))
    weights_id = cursor.lastrowid
    db.commit()
    cursor.close()
    db.close()
    return Result(True, "Vector created successfully", {"weights_id": weights_id})


def get_scenario_weights(scenario_id: int) -> list:
    scenarios = []
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Scenario_Weights WHERE scenario_id = %s', (scenario_id,))
    for id, scenario_id, criterion_id, size, in_progress in cursor:
        scenarios.append(ScenarioWeights(scenario_id, criterion_id, size, in_progress, id))
    cursor.close()
    db.close()
    return scenarios


def get_final_scenario_weights(scenario_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Scenario_Weights WHERE scenario_id = %s AND criterion_id = 0 AND in_progress = 0", (scenario_id,))
    for id, scenario_id, criterion_id, size, in_progress in cursor:
        values = get_vector_elements_values(id)
        if values:
            return Result(True, "Weight id found", {'values': values})
    cursor.close()
    db.close()
    return Result(False, "Weight id not found")


def delete_scenario_weights_with_elements(scenario_id: int):
    scenario_weights = get_scenario_weights(scenario_id)
    for weight in scenario_weights:
        delete_element(weight.id)
