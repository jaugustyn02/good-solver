from datetime import datetime, timedelta
from helpers.database import get_mysql_connection as get_db
from helpers.result import OperationResult as Result
from models.experts import Expert, get_expert_id, create_expert
from models.alternatives import Alternative, create_alternative, get_alternative_id
from models.criterions import Criteria, create_criteria, get_criteria_id
from models.scales import Scale, create_scale, get_scale_id

class Ranking:
    def __init__(self, name, ranking_method, aggregation_method, completeness_required, start_date, end_date, id=None):
        self.id = id
        self.name = name
        self.ranking_method = ranking_method
        self.aggregation_method = aggregation_method
        self.completeness_required = completeness_required
        self.start_date = start_date
        self.end_date = end_date

def delete_ranking(name):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Models WHERE name = %s', (name,))
    if cursor.fetchone() is not None:
        return Result(False, 'Model does not exist!')

    cursor.execute('DELETE FROM Model_Alternatives WHERE model_id = %s', (alternative_id,))
    db.commit()
    cursor.close()
    db.close()
    return Result(True, "Alternative deleted successfully")


def all_rankings():
    rankings = []
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Models')
    for id, name, ranking_method, aggregation_method, completeness_required, start_date, end_date in cursor:
        rankings.append(name)
    cursor.close()
    db.close()
    return rankings

def get_ranking(ranking_name):
    return ["Film 1", "Film 2", "Film 3"]
    db = get_db()
    cursor = db.cursor()
    data = []
    cursor.execute("SELECT * FROM Models WHERE name like '%s'" % ranking_name)
    for id, name, mail in cursor:
        ...
    cursor.close()
    db.close()
    return data

def create_ranking(name, alternatives, criterions, experts, start_date, end_date, scale):
    if name == "" or alternatives == "" or criterions == "" or scale == "":
        return Result(False, "Not enough data provided")
    if start_date == "":
        start_date = datetime.now()
    if end_date == "":
        end_date = datetime.now() + timedelta(days=1)
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO Models (name, ranking_method, aggregation_method, completeness_required, start_date, end_date) VALUES (%s, %s, %s, %s, %s, %s)',
        (name, "EVM", "AIJ", True, start_date, end_date))
    db.commit()
    cursor.close()
    cursor = db.cursor()
    sql = ("SELECT model_id FROM Models WHERE name like '%s'" % name)
    cursor.execute(sql)
    model_id_ = 1
    if cursor.fetchone() is None:
        return Result(False, 'Something went wrong')
    for model_id in cursor:
        model_id_ = model_id
    cursor.close()
    cursor = db.cursor()
    for alternative in alternatives.split(", "):
        alt_id = get_alternative_id(alternative)
        if not alt_id or (type(alt_id) is Result and not alt_id.success):
            create_alternative(Alternative(alternative, ""))
            alt_id = get_alternative_id(alternative)
        cursor.execute(
            'INSERT INTO Model_Alternatives (model_id, alternative_id) VALUES (%s, %s)',
            (model_id_[0], alt_id))
        db.commit()
    cursor.close()
    cursor = db.cursor()
    for criteria in criterions.split(", "):
        criteria_id = get_criteria_id(criteria)
        if not criteria_id or (type(criteria_id) is Result and not criteria_id.success):
            create_criteria(Criteria(None, criteria, ""))
            criteria_id = get_criteria_id(criteria)
        cursor.execute(
            'INSERT INTO Model_Criterias (model_id, criterion_id) VALUES (%s, %s)',
            (model_id_[0], criteria_id))
        db.commit()
    cursor.close()
    cursor = db.cursor()
    for expert in experts.split(", "):
        expert_id = get_expert_id(expert)
        if not expert_id:
            create_expert(Expert(expert, ""))
            expert_id = get_expert_id(expert)
        cursor.execute(
            'INSERT INTO Model_Experts (ranking_id, expert_id) VALUES (%s, %s)',
            (model_id_[0], expert_id))
        db.commit()
    cursor.close()
    cursor = db.cursor()
    if scale == "":
        scale = "1 2 3 4 5 6 7 8 9"
    scale_id = get_scale_id(scale)
    if not scale_id or (type(scale_id) is Result and not scale_id.success):
        create_scale(Scale(1, scale))
        scale_id = get_scale_id(scale)
    cursor.execute(
        'INSERT INTO Model_Scales (model_id, scale_id) VALUES (%s, %s)',
        (model_id_[0], scale_id))
    db.commit()
    cursor.close()
    db.close()
    return Result(True, "Ranking created successfully")
