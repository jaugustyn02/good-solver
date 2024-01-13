from helpers.database import get_mysql_connection as get_db
from helpers.result import OperationResult as Result
# from models.scenario_data import get_scenario_data
from models.matrix_element import get_matrix_element, MatrixElement, create_matrix_element
from models.criterions import is_parent_criterion
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


def find_empty_matrix_field(expert_id: int, scenario_id: int, criterias: list, alternatives: list) -> Result:
    data_id = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Scenario_Data WHERE scenario_id like '%s'" % scenario_id)
    for id, scenario_id, in_progress in cursor:
        cursor.close()
        db.close()
        data_id = id
        break
    
    for criterion in criterias:
        data_matrix = get_data_matrix(data_id, expert_id, criterion.id)
        if data_matrix.success:
            data_matrix = data_matrix.data['data']
            if not is_parent_criterion(criterion.id).success:
                for alt1 in alternatives:
                    for alt2 in alternatives:
                        if alt1.id != alt2.id:
                            matrix_element = get_matrix_element(data_matrix.id, alt1.id, alt2.id)
                            if matrix_element.success is False:
                                return Result(True, "Successfully found matrix elements", {'data': [alt1.id, alt2.id, criterion]})
            else:
                for cri1 in criterias:
                    for cri2 in criterias:
                        if cri1.id != cri2.id and cri1.id != criterion.id and cri2.id != criterion.id and cri1.parent_id == cri2.parent_id and cri1.parent_id == criterion.id:
                            matrix_element = get_matrix_element(data_matrix.id, cri1.id, cri2.id)
                            if matrix_element.success is False:
                                return Result(True, "Successfully found matrix elements",
                                              {'data': [cri1.id, cri2.id, criterion]})
    return Result(False, "No empty matrix fields")


def complete_all_other_fields(expert_id: int, scenario_id: int, criterias: list, alternatives: list) -> Result:
    data_id = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Scenario_Data WHERE scenario_id like '%s'" % scenario_id)
    for id, scenario_id, in_progress in cursor:
        cursor.close()
        db.close()
        data_id = id
        break

    for criterion in criterias:
        data_matrix = get_data_matrix(data_id, expert_id, criterion.id)
        if data_matrix.success:
            data_matrix = data_matrix.data['data']
            if not is_parent_criterion(criterion.id).success:
                for alt1 in alternatives:
                    create_matrix_element(MatrixElement(data_matrix.id, alt1.id, alt1.id, 1.0))
            else:
                for cri1 in criterias:
                    create_matrix_element(MatrixElement(data_matrix.id, cri1.id, cri1.id, 1.0))
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