from helpers.database import get_mysql_connection as get_db
from helpers.result import OperationResult as Result
from models.scenarios import Scenario, create_scenario, get_scenario_data_id, get_scenario_id, set_scenario_in_progress
from models.alternatives import Alternative, create_alternative, delete_alternative
from models.criterions import Criterion, create_criterion, delete_criterion
from models.scales import Scale, create_scale, delete_scale, default_scales
from models.data_matrices import create_expert_matrices, find_empty_matrix_field
from models.scenario_data import set_scenario_data_in_progress
from models.weights_vector_element import create_weights_vector_element
import models.scenario_weights as scenario_weights
from datetime import datetime
from models.AIP import AIP
from models.AIJ import AIJ
import numpy as np


class Model:
    def __init__(self, name, ranking_method, aggregation_method, completeness_required, start_date, end_date, id=None):
        self.id = id
        self.name = name
        self.ranking_method = ranking_method
        self.aggregation_method = aggregation_method
        self.completeness_required = completeness_required
        self.start_date = start_date
        self.end_date = end_date
        
    def get_alternatives(self):
        return get_model_alternatives(self.id).data['alternatives']
    
    def get_criterias(self):
        return get_model_criterias(self.id).data['criterias']

    def get_experts(self):
        return get_model_experts_id(self.id)
    
    def add_alternative(self, alternative: Alternative):
        return add_model_alternative(self.id, alternative)
    
    def delete_alternative(self, alternative_id: int) -> Result:
        return delete_model_alternative(self.id, alternative_id)
    
    def add_criterion(self, criterion: Criterion):
        return add_model_criterion(self.id, criterion)
    
    def delete_criterion(self, criterion_id: int) -> Result:
        return delete_model_criterion(self.id, criterion_id)
    
    def get_scales(self):
        return get_model_scales(self.id).data['scales']

    def confirm(self) -> Result:
        return confirm_model(self.id)

    def finalize(self) -> Result:
        return finalize_model(self.id)

    def delete(self) -> Result:
        return delete_model_data(self.id)
        
        
def add_model(model: Model) -> Result:
    if model.name == "":
        return Result(False, "Ranking name cannot be empty")
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO Models (name, ranking_method, aggregation_method, completeness_required, start_date, end_date) VALUES (%s, %s, %s, %s, %s, %s)', (model.name, model.ranking_method, model.aggregation_method, model.completeness_required, model.start_date, model.end_date))
    db.commit()
    model_id = cursor.lastrowid
    cursor.close()
    db.close()
    scenario = Scenario(model_id)
    scenario_result = create_scenario(scenario)
    scenario_id = scenario_result.data['scenario_id']
    
    # Add root criteria
    root_criterion = Criterion(None, "root", "")
    add_model_criterion(model_id, root_criterion)
    
    # Add default scales
    add_default_scales(model_id)
    
    return Result(True, "Model created successfully", {"model_id": model_id, "scenario_id": scenario_id})


def delete_model_data(model_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    alternative_ids = []
    criterion_ids = []
    scale_ids = []
    
    cursor.execute('SELECT alternative_id FROM Model_Alternatives WHERE model_id = %s', (model_id,))
    for alternative_id in cursor:
        alternative_ids.append(alternative_id[0])
    
    cursor.execute('SELECT criterion_id FROM Model_Criterias WHERE model_id = %s ORDER BY criterion_id DESC', (model_id,))
    for criterion_id in cursor:
        criterion_ids.append(criterion_id[0])
    
    cursor.execute('SELECT scale_id FROM Model_Scales WHERE model_id = %s', (model_id,))
    for scale_id in cursor:
        scale_ids.append(scale_id[0])
        
    cursor.execute('DELETE FROM Model_Alternatives WHERE model_id = %s', (model_id,))
    cursor.execute('DELETE FROM Model_Criterias WHERE model_id = %s', (model_id,))
    cursor.execute('DELETE FROM Model_Scales WHERE model_id = %s', (model_id,))
    cursor.execute('DELETE FROM Model_Experts WHERE ranking_id = %s', (model_id,))
    
    for alternative_id in alternative_ids:
        cursor.execute('DELETE FROM Alternatives WHERE alternative_id = %s', (alternative_id,))
    for criterion_id in criterion_ids:
        cursor.execute('DELETE FROM Criterias WHERE criterion_id = %s', (criterion_id,))
    for scale_id in scale_ids:
        cursor.execute('DELETE FROM Scales WHERE scale_id = %s', (scale_id,))
        
    db.commit()
    cursor.close()
    
    return Result(True, "Model data deleted successfully")


def delete_model(model_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM Models WHERE model_id = %s', (model_id,))
    db.commit()
    cursor.close()
    db.close()
    
    return Result(True, "Model deleted successfully")


def finalize_model(model_id: int) -> Result:
    scenario = get_scenario_id(model_id)
    if not scenario.success:
        return Result(False, "Scenario not found")
    scenario_id = scenario.data['scenario_id']
    
    result = set_scenario_in_progress(scenario_id, False)
    if not result.success:
        return Result(False, "Scenario couldn't be finalized")
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE Models SET end_date = %s WHERE model_id = %s', (datetime.now(), model_id))
    db.commit()
    cursor.close()
    db.close()
    
    model = get_model(model_id).data['model']
    agg_method = get_model_aggregation_method(model_id).data['agg_method']
    if agg_method == 'aip':
        ranking: np.ndarray = AIP(model)
    elif agg_method == 'aij':
        ranking: np.ndarray = AIJ(model)
        
    
    # Add result to scenario_weights
    weights = scenario_weights.ScenarioWeights(scenario_id, 0, len(ranking), False)
    weights_id = scenario_weights.create_scenario_weights(weights).data['weights_id']
    alternatives = get_model_alternatives(model_id).data['alternatives']
    for i, alternative in enumerate(alternatives):
        create_weights_vector_element(weights_id, alternative.id, float(ranking[i]))
    
    
    return Result(True, "Model finalized successfully")


def confirm_model(model_id: int):
    scenario_id = get_scenario_id(model_id).data['scenario_id']
    return set_scenario_data_in_progress(scenario_id, True)


def get_model(model_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Models WHERE model_id like '%s'" % model_id)
    for id, name, ranking_method, aggregation_method, completeness_required, start_date, end_date in cursor:
        cursor.close()
        db.close()
        model = Model(name, ranking_method, aggregation_method, completeness_required, start_date, end_date, id)
        return Result(True, "Model found", {'model': model})
    return Result(False, 'Model is not present!')

def get_model_name(model_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM Models WHERE model_id like '%s'" % model_id)
    for name in cursor:
        cursor.close()
        db.close()
        return Result(True, "Model found", {"model_name": name[0]})
    return Result(False, 'Model is not present!')


def get_model_id(model_name: str) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT model_id FROM Models WHERE name like '%s'" % model_name)
    for model_id in cursor:
        cursor.close()
        db.close()
        return Result(True, "Model found", {"model_id": model_id[0]})
    return Result(False, 'Model is not present!')


def get_model_alternatives(model_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Alternatives WHERE alternative_id IN (SELECT alternative_id FROM Model_Alternatives WHERE model_id like '%s')" % model_id)
    alternatives = []
    for id, name, description in cursor:
        alternatives.append(Alternative(name, description, id))
    cursor.close()
    db.close()
    return Result(True, "Alternatives found", {"alternatives": alternatives})

def get_model_criterias(model_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Criterias WHERE criterion_id IN (SELECT criterion_id FROM Model_Criterias WHERE model_id like '%s')" % model_id)
    criteria = []
    for id, parent_id, name, description in cursor:
        criteria.append(Criterion(parent_id, name, description, id))
    cursor.close()
    db.close()
    return Result(True, "Criteria found", {"criterias": criteria})

def get_model_scales(model_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Scales WHERE scale_id IN (SELECT scale_id FROM Model_Scales WHERE model_id like '%s')" % model_id)
    scales = []
    for id, value, description in cursor:
        scales.append(Scale(value, description, id))
    cursor.close()
    db.close()
    return Result(True, "Scales found", {"scales": scales})


def add_model_alternative(model_id: int, alternative: Alternative) -> Result:
    create_result = create_alternative(alternative)
    if create_result.success:
        alternative_id = create_result.data['alternative_id']
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO Model_Alternatives (model_id, alternative_id) VALUES (%s, %s)', (model_id, alternative_id))
        db.commit()
        cursor.close()
        db.close()
        return Result(True, "Alternative added successfully", {"alternative_id": alternative_id})
    return create_result

def delete_model_alternative(model_id: int, alternative_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM Model_Alternatives WHERE model_id = %s AND alternative_id = %s', (model_id, alternative_id))
    db.commit()
    cursor.close()
    db.close()
    return delete_alternative(alternative_id)

def add_model_criterion(model_id: int, criterion: Criterion) -> Result:
    create_result = create_criterion(criterion)
    if create_result.success:
        criterion_id = create_result.data['criterion_id']
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO Model_Criterias (model_id, criterion_id) VALUES (%s, %s)', (model_id, criterion_id))
        db.commit()
        cursor.close()
        db.close()
        return Result(True, "Criterion added successfully", {"criterion_id": criterion_id})
    return create_result

def delete_model_criterion(model_id: int, criterion_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM Model_Criterias WHERE model_id = %s AND criterion_id = %s', (model_id, criterion_id))
    db.commit()
    cursor.close()
    db.close()
    return delete_criterion(criterion_id)

def add_model_scale(model_id: int, scale: Scale) -> Result:
    create_result = create_scale(scale)
    if create_result.success:
        scale_id = create_result.data['scale_id']
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO Model_Scales (model_id, scale_id) VALUES (%s, %s)', (model_id, scale_id))
        db.commit()
        cursor.close()
        db.close()
        return Result(True, "Scale added successfully", {"scale_id": scale_id})
    return create_result

def delete_model_scale(model_id: int, scale_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM Model_Scales WHERE model_id = %s AND scale_id = %s', (model_id, scale_id))
    db.commit()
    cursor.close()
    db.close()
    return delete_scale(scale_id)

def add_default_scales(model_id: int) -> Result:
    for scale in default_scales:
        add_model_scale(model_id, scale)
    return Result(True, "Default scales added successfully")


def add_expert_to_model(model_id: int, expert_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT * FROM Model_Experts WHERE ranking_id = %s AND expert_id = %s', (model_id, expert_id))
    if cursor.fetchone() is not None:
        return Result(False, 'You have already joined this survey')
    
    cursor.execute('INSERT INTO Model_Experts (ranking_id, expert_id) VALUES (%s, %s)', (model_id, expert_id))
    db.commit()
    cursor.close()
    db.close()
    
    # Create expert data matrices
    alternatives = get_model_alternatives(model_id).data['alternatives']
    criterias = get_model_criterias(model_id).data['criterias']
    
    scenario_id = get_scenario_id(model_id).data['scenario_id']
    data_id = get_scenario_data_id(scenario_id).data['data_id']
    
    result = create_expert_matrices(data_id, expert_id, alternatives, criterias)
    if not result.success:
        return result
    
    return Result(True, "You have joined the survey successfully")


def get_model_experts_id(model_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Experts WHERE expert_id IN (SELECT expert_id FROM Model_Experts WHERE ranking_id = %s)',(model_id,))
    experts_id = []
    for id, name, address in cursor:
        experts_id.append(id)
    cursor.close()
    db.close()
    return experts_id


def count_experts_in_model(model_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM Model_Experts WHERE ranking_id = %s', (model_id,))
    for count in cursor:
        cursor.close()
        db.close()
        return Result(True, "Experts counted", {"expert_count": count[0]})
    return Result(False, "No experts found")


def count_alternatives_in_model(model_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM Model_Alternatives WHERE model_id = %s', (model_id,))
    for count in cursor:
        cursor.close()
        db.close()
        return Result(True, "Alternatives counted", {"alternative_count": count[0]})
    return Result(False, "No alternatives found")


def surveys_completed_count(model_id: int) -> int:
    count = 0
    model = get_model(model_id).data['model']
    experts_id = get_model_experts_id(model_id)
    scenario_id = get_scenario_id(model_id).data['scenario_id']
    for expert_id in experts_id:
        res = find_empty_matrix_field(expert_id, scenario_id, model.get_criterias(), model.get_alternatives())
        if not res.success:
            count += 1
    return count


def get_model_aggregation_method(model_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT aggregation_method FROM Models WHERE model_id = %s', (model_id,))
    for aggregation_method in cursor:
        cursor.close()
        db.close()
        return Result(True, "Aggregation method found", {"agg_method": aggregation_method[0]})
    return Result(False, "Aggregation method not found")