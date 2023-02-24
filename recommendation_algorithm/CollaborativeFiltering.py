import numpy as np


class CollaborativeFiltering:
    def __init__(self, ratings):
        """
        initializes the class with the user-item rating matrix, creates a user-item matrix,
        and creates a similarity matrix based on the user-item matrix.
        """
        self.ratings = ratings
        self.users = np.unique(ratings[:, 0])
        self.items = np.unique(ratings[:, 1])
        self.user_item_matrix = self._create_user_item_matrix(ratings)
        self.similarity_matrix = self._create_similarity_matrix()

    def _create_user_item_matrix(self, ratings):
        """
        creates a user-item matrix from the ratings data, where the rows represent users,
        the columns represent items, and the entries represent the ratings given by the users to the items.
        """
        user_item_matrix = np.zeros((len(self.users), len(self.items)))
        for user, item, rating in ratings:
            user_index = np.where(self.users == user)[0][0]
            item_index = np.where(self.items == item)[0][0]
            user_item_matrix[user_index, item_index] = rating
        return user_item_matrix

    def _create_similarity_matrix(self):
        """
        creates a similarity matrix between users based on their ratings of items.
        The similarity between two users is computed using the Pearson correlation coefficient
        between their ratings of the items that they have both rated.
        """
        similarity_matrix = np.zeros((len(self.users), len(self.users)))
        for i in range(len(self.users)):
            for j in range(len(self.users)):
                if i != j:
                    user1_items = self.user_item_matrix[i, :]
                    user2_items = self.user_item_matrix[j, :]
                    common_items = np.logical_and(user1_items != 0, user2_items != 0)
                    if np.sum(common_items) > 0:
                        user1_ratings = user1_items[common_items]
                        user2_ratings = user2_items[common_items]
                        similarity = np.corrcoef(user1_ratings, user2_ratings)[0, 1]
                        similarity_matrix[i, j] = similarity
        return similarity_matrix

    def _get_user_ratings(self, user):
        """
        returns the rating vector for a given user.
        """
        user_index = np.where(self.users == user)[0][0]
        return self.user_item_matrix[user_index, :]

    def _predict_rating(self, user, item):
        """
        predicts the rating that a user would give to an item based on the ratings of other
        users who have rated that item. The prediction is made by multiplying the ratings of the
        other users by their similarity scores with the target user and taking the weighted average of the resulting ratings.
        """
        user_index = np.where(self.users == user)[0][0]
        item_index = np.where(self.items == item)[0][0]
        user_ratings = self.user_item_matrix[:, item_index]
        similarity_scores = self.similarity_matrix[user_index, :]
        weighted_ratings = user_ratings * similarity_scores
        weighted_ratings = weighted_ratings[weighted_ratings != 0]
        if np.sum(np.abs(weighted_ratings)) == 0:
            return 0
        else:
            return np.sum(weighted_ratings) / np.sum(np.abs(similarity_scores))

    def recommend_workers(self, user, n=5):
        """
        recommends a set of n items to a given user based on their ratings of other items.
        It does this by first finding the unrated items for the user, predicting their ratings
        using the _predict_rating function, and then returning the top n items with the highest predicted ratings.
        """
        user_ratings = self._get_user_ratings(user)
        unrated_items = np.where(user_ratings == 0)[0]
        predicted_ratings = []
        for item in unrated_items:
            rating = self._predict_rating(user, self.items[item])
            predicted_ratings.append((self.items[item], rating))
        top_n = sorted(predicted_ratings, key=lambda x: x[1], reverse=True)[:n]
        return top_n
