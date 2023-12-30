from helpers.database import get_mysql_connection as get_db
from helpers.result import OperationResult as Result


class Scale:
    def __init__(self, value, description, id=None):
        self.id = id
        self.value = value
        self.description = description

def create_scale(scale: Scale) -> dict:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO Scales (value, description) VALUES (%s, %s)', (scale.value, scale.description))
    db.commit()
    cursor.close()
    db.close()
    return Result(True, "Scale created successfully")

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