from helpers.database import get_mysql_connection as get_db
from helpers.result import OperationResult as Result
from models.alternatives import get_alternative


class WeightsVectorElement:
    def __init__(self, weights_id, column, value, id=None):
        self.id = id
        self.weights_id = weights_id
        self.column = column
        self.value = value


def create_weights_vector_element(weights_id: int, column: int, value: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO Weights_Vector_Element (weights_id, `column`, value) VALUES (%s, %s, %s)',
                   (weights_id, column, value))
    db.commit()
    cursor.close()
    db.close()
    return Result(True, "Element created successfully")


def get_vector_elements(weights_id: int):
    vector_elements = []
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM WeightsVectorElement WHERE weights_id = %s', (weights_id,))
    for id, weights_id, column, value in cursor:
        vector_elements.append(WeightsVectorElement(weights_id, column, value, id))
    cursor.close()
    db.close()
    return vector_elements


def get_vector_elements_values(weights_id: int):
    vector_elements = get_vector_elements(weights_id)
    values = []
    for vector_element in vector_elements:
        alternative = get_alternative(vector_element.column)
        if alternative.success:
            values.append([alternative.name, vector_element.value])
    return vector_elements
