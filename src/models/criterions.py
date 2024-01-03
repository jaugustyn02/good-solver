from helpers.database import get_mysql_connection as get_db
from helpers.result import OperationResult as Result


class Criterion:
    def __init__(self, parent_id, name, description, id=None):
        self.id = id
        self.parent_id = parent_id
        self.name = name
        self.description = description

def create_criterion(criterion: Criterion) -> dict:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO Criterias (parent_criterion, name, description) VALUES (%s, %s, %s)', (criterion.parent_id, criterion.name, criterion.description))
    criterion_id = cursor.lastrowid
    db.commit()
    cursor.close()
    db.close()
    return Result(True, "Alternative created successfully", {"criterion_id": criterion_id})

def delete_criterion(criterion_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT * FROM Model_Criterias WHERE criterion_id = %s', (criterion_id,))
    if cursor.fetchone() is not None:
        return Result(False, 'Criterion is being used in a model!')
    
    cursor.execute('DELETE FROM Criterias WHERE criterion_id = %s', (criterion_id,))
    db.commit()
    cursor.close()
    db.close()
    return Result(True, "Alternative deleted successfully")

# def get_criteria_id(name_):
#     db = get_db()
#     cursor = db.cursor()
#     cursor.execute("SELECT * FROM Criterias WHERE name = %s", (name_,))
#     if cursor.fetchone() is None:
#         return Result(False, 'Criteria is not present!')
#     for criterion_id, parent_criterion, name, description in cursor:
#         cursor.close()
#         db.close()
#         return criterion_id