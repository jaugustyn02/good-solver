from helpers.database import get_mysql_connection as get_db
from helpers.result import OperationResult as Result
from models.matrix_element import get_matrix_element, MatrixElement, create_matrix_element
from models.criterions import is_parent_criterion
from collections import defaultdict
from models.alternatives import Alternative
from models.criterions import Criterion
import numpy as np


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


def get_data_matrix(data_id: int, expert_id: int, criterion_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Data_Matrices WHERE data_id = '%s' AND expert_id = '%s' AND criterion_id = '%s'" % (data_id, expert_id, criterion_id))
    for id, data_id, expert_id, criterion_id, size in cursor:
        cursor.close()
        db.close()
        data = DataMatrix(data_id, expert_id, criterion_id, size,id)
        return Result(True, "Data matrix found", {'data': data})
    return Result(False, 'Data matrix is not present!')


def get_all_data_matrix_elements(matrix_id: int, size: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Data_Matrix_Element WHERE matrix_id = '%s'" % matrix_id)
    matrix_elements = []
    for id, matrix_id, row, column, value in cursor:
        element = MatrixElement(matrix_id, row, column, value, id)
        matrix_elements.append(element)
    cursor.close()
    db.close()
    if not matrix_elements:
        return Result(False, 'Data matrix is not complete!')
    matrix_elements = sorted(matrix_elements, key=lambda x: (x.row, x.column))
    data = [[0 for _ in range(size)] for _ in range(size)]
    for i in range(size):
        for j in range(size):
            data[i][j] = matrix_elements[i*size + j].value
    return Result(True, "Data matrix found", {'data': np.array(data)})


def find_empty_matrix_field(expert_id: int, data_id: int, model_id: int) -> Result:
    data, alternatives, criterias = get_all_matrix_data(expert_id, data_id, model_id)
    cri_parent_ids = set([cri.parent_id for cri in criterias])
    for criterion in criterias:
        if not criterion.id in cri_parent_ids:
            for alt1 in alternatives:
                for alt2 in alternatives:
                    if alt1.id != alt2.id:
                        if (alt1.id, alt2.id) not in data[criterion.id]:
                            return Result(True, "Successfully found matrix elements", {'data': [alt1.id, alt2.id, criterion], 'type':'alternative'})
        else:
            for cri1 in criterias:
                for cri2 in criterias:
                    if cri1.id != cri2.id and cri1.parent_id == criterion.id and cri2.parent_id == criterion.id:
                        if (cri1.id, cri2.id) not in data[criterion.id]:
                            return Result(True, "Successfully found matrix elements",
                                            {'data': [cri1.id, cri2.id, criterion], 'type':'criteria'})
    return Result(False, "No empty matrix fields")


def get_all_matrix_data(expert_id: int, data_id: int, model_id: int):
    db = get_db()
    cursor = db.cursor()
    data = defaultdict(set)
    cursor.execute("SELECT criterion_id, `row`, `column` FROM Data_Matrix_Element as el INNER JOIN Data_Matrices as mat ON mat.matrix_id = el.matrix_id WHERE data_id like '%s' AND expert_id like '%s'" % (data_id, expert_id))
    for criterion_id, row, column in cursor:
        data[criterion_id].add((row, column))

    cursor.execute("SELECT * FROM Alternatives WHERE alternative_id IN (SELECT alternative_id FROM Model_Alternatives WHERE model_id like '%s')" % model_id)
    alternatives = []
    for id, name, description in cursor:
        alternatives.append(Alternative(name, description, id))

    cursor.execute("SELECT * FROM Criterias WHERE criterion_id IN (SELECT criterion_id FROM Model_Criterias WHERE model_id like '%s')" % model_id)
    criteria = []
    for id, parent_id, name, description in cursor:
        criteria.append(Criterion(parent_id, name, description, id))
    
    cursor.close()
    db.close()
    return data, alternatives, criteria


def complete_all_other_fields(expert_id: int, data_id: int, model_id: int) -> Result:

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Alternatives WHERE alternative_id IN (SELECT alternative_id FROM Model_Alternatives WHERE model_id like '%s')" % model_id)
    alternatives = []
    for id, name, description in cursor:
        alternatives.append(Alternative(name, description, id))

    cursor.execute("SELECT * FROM Criterias WHERE criterion_id IN (SELECT criterion_id FROM Model_Criterias WHERE model_id like '%s')" % model_id)
    criterias = []
    for id, parent_id, name, description in cursor:
        criterias.append(Criterion(parent_id, name, description, id))

    cri_parent_ids = set([cri.parent_id for cri in criterias])
    for criterion in criterias:
        cursor.execute("SELECT matrix_id FROM Data_Matrices WHERE data_id = '%s' AND expert_id = '%s' AND criterion_id = '%s'" % (data_id, expert_id, criterion.id))
        matrix_id = cursor.fetchone()[0]
        if not criterion.id in cri_parent_ids:
            for alt1 in alternatives:
                cursor.execute("INSERT INTO Data_Matrix_Element (matrix_id, `row`, `column`, value) VALUES ('%s', '%s', '%s', '%s')" % (matrix_id, alt1.id, alt1.id, 1.0))
                db.commit()
        else:
            for cri1 in criterias:
                cursor.execute("INSERT INTO Data_Matrix_Element (matrix_id, `row`, `column`, value) VALUES ('%s', '%s', '%s', '%s')" % (matrix_id, cri1.id, cri1.id, 1.0))
                db.commit()

    cursor.close()
    db.close()
    return Result(False, "No empty matrix fields")

def delete_matrix(matrix_id: int) -> Result:
    # Delete matrix elements
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM Data_Matrix_Element WHERE matrix_id = %s', (matrix_id,))
    db.commit()
    cursor.close()
    # Delete matrix
    cursor = db.cursor()
    cursor.execute('DELETE FROM Data_Matrices WHERE matrix_id = %s', (matrix_id,))
    db.commit()
    cursor.close()
    db.close()
    return Result(True, "Matrix deleted successfully")