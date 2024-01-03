from helpers.database import get_mysql_connection as get_db
from helpers.result import OperationResult as Result
from models.models import Model

class Expert:
    def __init__(self, name, mail, id=None):
        self.id = id
        self.name = name
        self.mail = mail
    
    def __str__(self):
        return f'Expert(id={self.id}, name={self.name}, mail={self.mail})'

def get_experts() -> list:
    experts = []
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Experts')
    for id, name, mail in cursor:
        experts.append(Expert(name, mail, id))
    cursor.close()
    db.close()
    return experts


def get_expert_id(name_):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Experts WHERE name like '%s'" % name_)
    for id, name, mail in cursor:
        cursor.close()
        db.close()
        return id
    
def check_email_occupation(email):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Experts WHERE address like '%s'" % email)
    for id, name, mail in cursor:
        cursor.close()
        db.close()
        return True
    return False

def validate_expert(expert: Expert) -> Result:
    if expert.name == "":
        return Result(False, "Expert name cannot be empty")
    if expert.mail == "":
        return Result(False, "Expert email cannot be empty")
    if "@" not in expert.mail:
        return Result(False, "Invalid email")
    if check_email_occupation(expert.mail):
        return Result(False, "Email already in use")
    return Result(True, "Expert is valid")

def create_expert(expert: Expert) -> Result:
    validation = validate_expert(expert)
    if not validation.success:
        return validation
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO Experts (name, address) VALUES (%s, %s)', (expert.name, expert.mail))
    expert_id = cursor.lastrowid
    db.commit()
    cursor.close()
    db.close()
    return Result(True, "Expert created successfully", {"expert_id": expert_id})
    
def delete_expert(expert_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT * FROM Model_Experts WHERE expert_id = %s', (expert_id,))
    if cursor.fetchone() is not None:
        return Result(False, 'Expert is being used in a model!')
    
    cursor.execute('DELETE FROM Experts WHERE expert_id = %s', (expert_id,))
    db.commit()
    cursor.close()
    db.close()
    return Result(True, "Expert deleted successfully")


def get_expert_name(expert_id: int) -> str:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT name FROM Experts WHERE expert_id = %s', (expert_id,))
    name = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return name

def get_expert_first_name(expert_id: int) -> str:
    return get_expert_name(expert_id).split()[0]


def get_expert_models_in_progress(expert_id: int) -> list:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Models WHERE model_id IN (SELECT ranking_id FROM Model_Experts WHERE expert_id = %s) AND end_date > NOW()', (expert_id,))
    models = []
    for id, name, ranking_method, aggregation_method, completeness_required, start_date, end_date in cursor:
        models.append(Model(name, ranking_method, aggregation_method, completeness_required, start_date, end_date, id))
    cursor.close()
    db.close()
    return models

def get_expert_models_ended(expert_id: int) -> list:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Models WHERE model_id IN (SELECT ranking_id FROM Model_Experts WHERE expert_id = %s) AND end_date < NOW()', (expert_id,))
    models = []
    for id, name, ranking_method, aggregation_method, completeness_required, start_date, end_date in cursor:
        models.append(Model(name, ranking_method, aggregation_method, completeness_required, start_date, end_date, id))
    cursor.close()
    db.close()
    return models