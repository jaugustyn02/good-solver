from helpers.database import get_mysql_connection as get_db
from helpers.result import OperationResult as Result

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

def create_expert(expert: Expert) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO Experts (name, address) VALUES (%s, %s)', (expert.name, expert.mail))
    db.commit()
    cursor.close()
    db.close()
    return Result(True, "Expert created successfully")
    
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