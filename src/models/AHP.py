import numpy as np
from models.criterions import Criterion, get_criteria_children, get_root_criterion_id
import helpers.matrix as mat

# Ranking methods
GMM = 'gmm'
# Aggregation methods
AIP = 'aip'
AIJ = 'aij'


def AHP(model_id: int, matrices: dict, rank_method: str = GMM) -> np.ndarray:
    root_criterion_id: int = int(get_root_criterion_id(model_id).data['criterion_id'])
    criteria_children = get_criteria_children(model_id).data['criteria_children']
    print(criteria_children)
    return _get_criterion_ranking(root_criterion_id, matrices, criteria_children, rank_method)
    
    
def _get_criterion_ranking(criterion_id: int, matrices: dict, criteria_children: dict, rank_method: str = GMM) -> np.ndarray:
    children = criteria_children[criterion_id]
    if len(children) == 0:
        return mat.matrix_to_vector(matrices[criterion_id], rank_method)
    else:
        children_rankings = [_get_criterion_ranking(child.id, matrices, criteria_children, rank_method) for child in children]
        rankings_matrix = mat.vectors_to_matrix(children_rankings, rowWise=False)
        current_criterion_vector = mat.matrix_to_vector(matrices[criterion_id], rank_method)
        return mat.matrix_vector_mul(rankings_matrix, current_criterion_vector)
