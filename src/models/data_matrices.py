from helpers.database import get_mysql_connection as get_db
from helpers.result import OperationResult as Result
from models.criterions import Criterion
from models.alternatives import Alternative
from collections import defaultdict

class DataMatrix:
    def __init__(self, data_id, expert_id, criterion_id, size, id=None):
        self.id = id
        self.data_id = data_id
        self.expert_id = expert_id
        self.criterion_id = criterion_id
        self.size = size


def create_matrix(dataMatrix: DataMatrix) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO Data_Matrices (data_id, expert_id, criterion_id, size) VALUES (%s, %s, %s, %s)', (dataMatrix.data_id, dataMatrix.expert_id, dataMatrix.criterion_id, dataMatrix.size))
    matrix_id = cursor.lastrowid
    db.commit()
    cursor.close()
    db.close()
    return Result(True, "Matrix created successfully", {"matrix_id": matrix_id})


def create_expert_matrices(data_id: int, expert_id: int, alternatives: list, criteria: list):
    alternatives_count = len(alternatives)
    
    criteria_children_count = defaultdict(int)
        
    for criterion in criteria:
        criteria_children_count[criterion.parent_id] += 1
        
    for criterion in criteria:
        size = criteria_children_count.get(criterion.id, alternatives_count)
        matrix = DataMatrix(data_id, expert_id, criterion.id, size)
        create_matrix(matrix)
    
    return Result(True, "Expert matrices created successfully")
        
    