from helpers.database import get_mysql_connection as get_db
from helpers.result import OperationResult as Result
from collections import defaultdict


class Criterion:
    def __init__(self, parent_id, name, description, id=None):
        self.id = id
        self.parent_id = parent_id
        self.name = name
        self.description = description

def create_criterion(criterion: Criterion) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO Criterias (parent_criterion, name, description) VALUES (%s, %s, %s)', (criterion.parent_id, criterion.name, criterion.description))
    criterion_id = cursor.lastrowid
    db.commit()
    cursor.close()
    db.close()
    return Result(True, "Alternative created successfully", {"criterion_id": criterion_id})


def is_parent_criterion(criterion_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Criterias WHERE parent_criterion = %s', (criterion_id,))
    if cursor.fetchone() is not None:
        return Result(True, "This is not a parent criterion")
    return Result(False, "This is not a parent criterion")


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


def get_criteria(criterion_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Criterias WHERE criterion_id = %s", (criterion_id,))
    for id, parent_criterion, name, description in cursor:
        criterion = Criterion(parent_criterion, name, description, id)
        cursor.close()
        db.close()
        return Result(True, 'Criteria found', {'criterion': criterion})
    return Result(False, 'Criteria is not present!')


# def get_criterion_children(criterion_id: int) -> Result:
#     db = get_db()
#     cursor = db.cursor()
#     cursor.execute("SELECT * FROM Criterias WHERE parent_criterion = %s", (criterion_id,))
#     criteria = []
#     for id, parent_criterion, name, description in cursor:
#         criteria.append(Criterion(parent_criterion, name, description, id))
#     cursor.close()
#     db.close()
#     return Result(True, 'Criteria found', {'criteria': criteria})


def get_criteria_children(model_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Criterias WHERE criterion_id IN (SELECT criterion_id FROM Model_Criterias WHERE model_id = %s)", (model_id,))
    criteria_children = defaultdict(list)
    for id, parent_criterion, name, description in cursor:
        if criteria_children[id] is None:
            criteria_children[id] = []
        criteria_children[parent_criterion].append(Criterion(parent_criterion, name, description, id))
    cursor.close()
    db.close()
    return Result(True, 'Criteria found', {'criteria_children': criteria_children})


def get_root_criterion_id(model_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Criterias WHERE parent_criterion IS NULL AND criterion_id IN (SELECT criterion_id FROM Model_Criterias WHERE model_id = %s )", (model_id,))
    for id, parent_criterion, name, description in cursor:
        cursor.close()
        db.close()
        return Result(True, 'Root criterion found', {'criterion_id': id})
    cursor.close()
    db.close()
    return Result(False, 'Root criterion is not present!')