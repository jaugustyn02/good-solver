from helpers.database import get_mysql_connection as get_db
from helpers.result import OperationResult as Result


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
    db.commit()
    cursor.close()
    db.close()
    return Result(True, "Matrix created successfully")

