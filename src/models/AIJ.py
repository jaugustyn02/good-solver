from models.scenarios import get_scenario_data_id, get_scenario_id
from models.data_matrices import get_data_matrix, get_all_data_matrix_elements
from helpers.matrix import aggregate_matrices
from models.AHP import AHP
import numpy as np


def AIJ(model) -> np.ndarray:
    experts_ids = model.get_experts()
    scenario_id = get_scenario_id(model.id).data['scenario_id']
    data_id = get_scenario_data_id(scenario_id).data['data_id']
    matrices = {}
    for criterion in model.get_criterias():
        matrix = []
        for expert_id in experts_ids:
            data_matrix = get_data_matrix(data_id, expert_id, criterion.id).data['data']
            matrix_ = get_all_data_matrix_elements(data_matrix.id, data_matrix.size)
            if matrix_.success:
                matrix.append(matrix_.data['data'])
        matrices[criterion.id] = aggregate_matrices(matrix, "gmm", False)
    return AHP(model.id, matrices, model.ranking_method)
