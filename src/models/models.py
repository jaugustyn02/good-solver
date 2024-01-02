from helpers.database import get_mysql_connection as get_db
from helpers.result import OperationResult as Result
from models.scenarios import Scenario, create_scenario
from models.alternatives import Alternative, create_alternative, delete_alternative
from models.criterions import Criterion, create_criterion, delete_criterion
from models.scales import Scale, create_scale, delete_scale, default_scales

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
    
    def finalize(self):
        # TODO
        return Result(False, "Finalizing not implemented yet")
    
    def delete(self):
        # TODO
        return Result(False, "Deleting not implemented yet")
        
        
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

def delete_model(model_id: int) -> Result:
    # TODO
    return Result(True, "Deleteting not available yet")

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
    return Result(True, "You have joined the survey successfully")

def count_experts_in_model(model_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM Model_Experts WHERE ranking_id = %s', (model_id,))
    for count in cursor:
        cursor.close()
        db.close()
        return Result(True, "Experts counted", {"expert_count": count[0]})
    return Result(False, "No experts found")