import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import cdist
from sklearn.preprocessing import normalize


def calculate_similarity_matrix(features1, features2, metric='cosine'):
    """
    Calculate the similarity matrix between two sets of feature vectors.

    Args:
        features1 (numpy.ndarray): Feature vectors of the first set.
        features2 (numpy.ndarray): Feature vectors of the second set.
        metric (str, optional): Similarity metric to use. Defaults to 'cosine'.

    Returns:
        numpy.ndarray: Similarity matrix.
    """
    features1 = np.array(features1)
    features1 = normalize(features1)
    features2 = normalize(features2)

    if metric == 'cosine':
        similarity_matrix = cosine_similarity(features1, features2)
    elif metric == 'euclidean':
        distance_matrix = cdist(features1, features2, metric='euclidean')
        similarity_matrix = 1 / (1 + distance_matrix)
    else:
        raise ValueError(f"Unsupported metric: {metric}")

    return similarity_matrix


def calculate_video_vector_similarity(video_vector_arr_1, video_vector_arr_2):
    """
    Calculate the average similarity between two sets of video vectors.

    Args:
        video_vector_arr_1 (list): List of video vectors for the first set.
        video_vector_arr_2 (list): List of video vectors for the second set.

    Returns:
        float: Average similarity between the two sets of video vectors.
    """
    features1 = np.array(video_vector_arr_1)
    features2 = np.array(video_vector_arr_2)

    similarity_matrix = calculate_similarity_matrix(
        features1, features2)
    max_similarity = np.max(similarity_matrix, axis=1)
    average_similarity = np.mean(max_similarity)
    return average_similarity
