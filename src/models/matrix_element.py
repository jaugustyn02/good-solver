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
    cursor.execute('INSERT INTO Data_Matrix_Element (matrix_id, row, `column`, value) VALUES (%s, %s, %s, %s)', (matrixElement.matrix_id, matrixElement.row, matrixElement.column, matrixElement.value))
    db.commit()
    cursor.close()
    db.close()
    return Result(True, "Matrix element created successfully")


def get_matrix_element(matrix_id: int, row: int, column: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Data_Matrix_Element WHERE matrix_id = %s AND row = %s AND `column` = %s", (matrix_id, row, column))
    for id, matrix_id, row, column, value in cursor:
        cursor.fetchall()
        cursor.close()
        db.close()
        data = MatrixElement(matrix_id, row, column, value,id)
        return Result(True, "Matrix element found", {'data': data})
    return Result(False, 'Matrix element is not present!')
