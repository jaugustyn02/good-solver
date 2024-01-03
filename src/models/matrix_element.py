from helpers.database import get_mysql_connection as get_db
from helpers.result import OperationResult as Result

class MatrixElement:
    def __init__(self, matrix_id, row, column, value, id=None):
        self.id = id
        self.matrix_id = matrix_id
        self.row = row
        self.column = column
        self.value = value
        

def create_matrix_element(matrixElement: MatrixElement) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO Matrix_Elements (matrix_id, row, column, value) VALUES (%s, %s, %s, %s)', (matrixElement.matrix_id, matrixElement.row, matrixElement.column, matrixElement.value))
    db.commit()
    cursor.close()
    db.close()
    return Result(True, "Matrix element created successfully")