from helpers.database import get_mysql_connection as get_db

class Expert:
    def __init__(self, name, mail, id=None):
        self.id = id
        self.name = name
        self.mail = mail
    
    def __str__(self):
        return f'Expert(id={self.id}, name={self.name}, mail={self.mail})'

def get_experts() -> list:
    experts = []
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Experts')
    for id, name, mail in cursor:
        experts.append(Expert(name, mail, id))
    cursor.close()
    db.close()
    return experts

def create_expert(expert: Expert) -> None:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO Experts (name, address) VALUES (%s, %s)', (expert.name, expert.mail))
    db.commit()
    cursor.close()
    db.close()
    
def delete_expert(expert_id: int) -> None:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM Experts WHERE expert_id = %s', (expert_id,))
    db.commit()
    cursor.close()
    db.close()