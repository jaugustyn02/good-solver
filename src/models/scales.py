from helpers.database import get_mysql_connection as get_db
from helpers.result import OperationResult as Result
from helpers.is_float import is_float


class Scale:
    def __init__(self, value: float, description: str, id=None):
        self.id = id
        self.value = value
        self.description = description

default_scales = [
    Scale(1.0, "Equal importance"),
    Scale(2.0, "Equal to moderate importance"),
    Scale(3.0, "Moderate importance"),
    Scale(4.0, "Moderate to strong importance"),
    Scale(5.0, "Strong importance"),
    Scale(6.0, "Strong to very strong importance"),
    Scale(7.0, "Very strong importance"),
    Scale(8.0, "Very strong to extreme importance"),
    Scale(9.0, "Extreme importance"),
]

def validate_scale(scale: Scale) -> Result:
    if not is_float(scale.value):
        return Result(False, "Scale value must be a float")
    if scale.description == "":
        return Result(False, "Scale description cannot be empty")
    return Result(True, "Scale is valid")

def create_scale(scale: Scale) -> dict:
    validation = validate_scale(scale)
    if not validation.success:
        return validation
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO Scales (value, description) VALUES (%s, %s)', (scale.value, scale.description))
    scale_id = cursor.lastrowid
    db.commit()
    cursor.close()
    db.close()
    return Result(True, "Scale created successfully", {"scale_id": scale_id})

def delete_scale(id: int) -> dict:
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM Scales WHERE scale_id = %s", (id,))
    if cursor.fetchone() is None:
        return Result(False, 'Scale is not present!')
    
    cursor.execute('DELETE FROM Scales WHERE scale_id = %s', (id,))
    db.commit()
    cursor.close()
    db.close()
    return Result(True, "Scale deleted successfully")

def get_scale_id(description):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Scales WHERE description like '%s'" % description)
    if cursor.fetchone() is None:
        return Result(False, 'Scale is not present!')
    for id, value, description in cursor:
        cursor.close()
        db.close()
        return id