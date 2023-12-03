from helpers.database import get_mysql_connection as get_db

class Ranking:
    def __init__(self, name, ranking_method, aggregation_method, completeness_required, start_date, end_date, id=None):
        self.id = id
        self.name = name
        self.ranking_method = ranking_method
        self.aggregation_method = aggregation_method
        self.completeness_required = completeness_required
        self.start_date = start_date
        self.end_date = end_date

def all_rankings():
    return ["Ranking1", "Ranking2", "Ranking3"]
    rankings = []
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Models')
    for id, name, ranking_method, aggregation_method, completeness_required, start_date, end_date in cursor:
        rankings.append(Ranking(name, ranking_method, aggregation_method, completeness_required, start_date, end_date, id).name)
    cursor.close()
    db.close()
    return rankings
    # return ["Ranking1", "Ranking2", "Ranking3"]

def get_ranking(ranking_name):
    return ["Film 1", "Film 2", "Film 3"]
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Models WHERE name like %d', ranking_name)
    # for id, name, mail in cursor:
    #     ...
    cursor.close()
    db.close()
    return ["Film 1", "Film 2", "Film 3"]

def create_ranking(alternatives, criterions, experts, start_date, end_date, scale):
    ...