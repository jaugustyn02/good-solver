import numpy as np
from models.scenarios import get_scenario_data_id, get_scenario_id
from models.data_matrices import get_data_matrix, get_all_data_matrix_elements
from models.AHP import AHP
from helpers.matrix import aggregate_vectors


def AIP(model) -> np.ndarray:
    experts_ids = model.get_experts()
    scenario_id = get_scenario_id(model.id).data['scenario_id']
    data_id = get_scenario_data_id(scenario_id).data['data_id']
    results = []
    for expert_id in experts_ids:
        matrix = {}
        for criterion in model.get_criterias():
            data_matrix = get_data_matrix(data_id, expert_id, criterion.id).data['data']
            matrix_ = get_all_data_matrix_elements(data_matrix.id, data_matrix.size)
            if matrix_.success:
                matrix[criterion.id] = matrix_.data['data']
        results.append(AHP(model.id, matrix, model.ranking_method))

    return aggregate_vectors(results, "gmm", False)

