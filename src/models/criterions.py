from helpers.database import get_mysql_connection as get_db
from helpers.result import OperationResult as Result


class Criteria:
    def __init__(self, parent_id, name, description, id=None):
        self.id = id
        self.parent_id = parent_id
        self.name = name
        self.description = description

def create_criteria(criteria: Criteria) -> dict:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO Criterias (parent_criterion, name, description) VALUES (%s, %s, %s)', (criteria.parent_id, criteria.name, criteria.description))
    db.commit()
    cursor.close()
    db.close()
    return Result(True, "Alternative created successfully")

def get_criteria_id(name_):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Criterias WHERE name = %s", (name_,))
    if cursor.fetchone() is None:
        return Result(False, 'Criteria is not present!')
    for criterion_id, parent_criterion, name, description in cursor:
        cursor.close()
        db.close()
        return criterion_id