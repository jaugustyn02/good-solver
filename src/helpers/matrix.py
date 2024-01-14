import numpy as np


def matrix_to_vector(matrix: np.ndarray, method: str, rowWise: bool = True, normalize: bool = True) -> np.ndarray:
    """
    Converts a matrix to a vector using the specified method.
    :param matrix: The matrix to convert.
    :param method: The method to use for conversion.
    :param rowWise: If true, the matrix is converted row-wise, otherwise column-wise.
    :param normalize: If true, the vector is normalized to sum to 1.
    :return: The converted vector.
    """
    if method == "gmm": # Geometric mean method
        if rowWise:
            vector = np.prod(matrix, axis=1)
            vector = vector ** (1 / matrix.shape[1])
        else:
            vector = np.prod(matrix, axis=0)
            vector = vector ** (1 / matrix.shape[0])
    else:
        raise ValueError("Invalid method specified.")
    if normalize:
        vector = vector / np.sum(vector)
    return vector


def vectors_to_matrix(vectors: list, rowWise: bool = True) -> np.ndarray:
    if rowWise:
        return np.array(vectors)
    else:
        return np.array(vectors).transpose()
    


def matrix_vector_mul(matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
    if matrix.shape[1] != vector.shape[0]:
        raise ValueError("Matrix and vector have incompatible dimensions: {} and {}.".format(matrix.shape, vector.shape))
    return np.dot(matrix, vector)


def aggregate_matrices(matrices: list, method: str, normalize: bool = False) -> np.ndarray:
    # aggregate list of matrices into one matrix using the specified method (i,j - matrix index, k - matrix number)
    # aggregated matrix: a_ij = method([m_ijk]) for all k for all i,j
    
    aggregated_matrix = np.zeros(matrices[0].shape)
    if method == "gmm": # Geometric mean method
        for i in range(matrices[0].shape[0]):
            for j in range(matrices[0].shape[1]):
                aggregated_matrix[i, j] = np.prod([matrix[i, j] for matrix in matrices]) ** (1 / len(matrices))
                
    if normalize:
        aggregated_matrix = aggregated_matrix / np.sum(aggregated_matrix)
    return aggregated_matrix


def aggregate_vectors(vectors: list, method: str, normalize: bool = False) -> np.ndarray:
    # aggregate list of vectors into one vector using the specified method (i - vector index, k - vector number)
    # aggregated vector: a_i = method([v_ik]) for all k for all i
    
    aggregated_vector = np.zeros(vectors[0].shape)
    if method == "gmm": # Geometric mean method
        for i in range(vectors[0].shape[0]):
            aggregated_vector[i] = np.prod([vector[i] for vector in vectors]) ** (1 / len(vectors))
                
    if normalize:
        aggregated_vector = aggregated_vector / np.sum(aggregated_vector)
    return aggregated_vector


if __name__ == "__main__":
    # Test
    matrix = np.array([[1, 2, 3], [4, 5, 6]])
    print(matrix)
    vector = matrix_to_vector(matrix, "gmm", rowWise=False, normalize=True)
    print(vector)
    print()
    print(matrix_vector_mul(matrix, vector))
    print()
    matrix2 = np.array([[2, 2, 3], [4, 5, 3]])
    print(aggregate_matrices([matrix, matrix2, matrix], "gmm", normalize=False))
    print()
    print(aggregate_vectors([vector, vector, vector], "gmm", normalize=False))
    
    # vectors to matrix
    print()
    print(vectors_to_matrix([vector, vector, vector], rowWise=False))