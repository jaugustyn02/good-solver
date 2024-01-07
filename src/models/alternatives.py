from helpers.database import get_mysql_connection as get_db
from helpers.result import OperationResult as Result


class Alternative:
    def __init__(self, name, description="Brak", id=None):
        self.id = id
        self.name = name
        self.description = description
    
    def __str__(self):
        return f'Alternative(id={self.id}, name={self.name}, description={self.description})'
    
    
def get_alternatives() -> list:
    alternatives = []
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Alternatives')
    for id, name, description in cursor:
        alternatives.append(Alternative(name, description, id))
    cursor.close()
    db.close()
    return alternatives


def get_alternative(alternative_id) -> Result:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Alternatives WHERE alternative_id = %s', (alternative_id,))
    for id, name, description in cursor:
        alternative = Alternative(name, description, id)
        cursor.close()
        db.close()
        return Result(True, 'Alternative found', {'alternative': alternative})
    cursor.close()
    db.close()
    return Result(False, 'Alternative is not present!')


def get_alternative_id(name_):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Alternatives WHERE name = %s", (name_,))
    if cursor.fetchone() is None:
        return Result(False, 'Alternative is not present!')
    for id, name, description in cursor:
        cursor.close()
        db.close()
        return id


def create_alternative(alternative: Alternative) -> dict:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO Alternatives (name, description) VALUES (%s, %s)', (alternative.name, alternative.description))
    alternative_id = cursor.lastrowid
    db.commit()
    cursor.close()
    db.close()
    return Result(True, "Alternative created successfully", {"alternative_id": alternative_id})
    

def delete_alternative(alternative_id: int) -> Result:
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT * FROM Model_Alternatives WHERE alternative_id = %s', (alternative_id,))
    if cursor.fetchone() is not None:
        return Result(False, 'Alternative is being used in a model!')
    
    cursor.execute('DELETE FROM Alternatives WHERE alternative_id = %s', (alternative_id,))
    db.commit()
    cursor.close()
    db.close()
    return Result(True, "Alternative deleted successfully")
