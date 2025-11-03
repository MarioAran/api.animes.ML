import pandas as pd
import numpy as np
import warnings
import mysql.connector
warnings.filterwarnings('ignore')

class AnimeRecommendationModel:
    def __init__(self):
        self.user_item_matrix = None
        self.anime_df = None
        self.ratings_df = None
        self.model_type = "collaborative_filtering"
        self.user = None
        self.password = None
        self.user_login = None
        self.cnx = None
    
    def login(self, appUser, appPassword):
        self.user = appUser
        self.password =appPassword
        try:
            cnx = mysql.connector.connect(
                host="127.0.0.1",
                port=3306,
                user=self.user,
                password=self.password,
                database="sys")
            print(f"{self.user} and {self.password}")
            return "Logged"
        except Exception as e:
            print({str(e)})
        
    def fit(self, ratings_df, anime_df, min_ratings=100):
        self.ratings_df = ratings_df.copy()
        self.anime_df = anime_df.copy()
        
        # Filtrar usuarios y animes con suficientes ratings
        user_rating_count = ratings_df['user_id'].value_counts()
        anime_rating_count = ratings_df['anime_id'].value_counts()
        
        filtered_users = user_rating_count[user_rating_count >= min_ratings].index
        filtered_animes = anime_rating_count[anime_rating_count >= min_ratings].index
        
        filtered_ratings = ratings_df[
            (ratings_df['user_id'].isin(filtered_users)) & 
            (ratings_df['anime_id'].isin(filtered_animes))
        ]
        
        # Crear matriz usuario-item
        self.user_item_matrix = filtered_ratings.pivot_table(
            index='user_id', 
            columns='anime_id', 
            values='rating', 
            fill_value=0
        )
        
        return f"Modelo entrenado con {len(filtered_users)} usuarios y {len(filtered_animes)} animes"
        
    def recommend(self, user_id, n_recommendations=10):
        # Verificar si el usuario existe
        if user_id not in self.user_item_matrix.index:
            raise ValueError(f"Usuario {user_id} no encontrado en el modelo")
        
        # Obtener índice del usuario
        user_idx = list(self.user_item_matrix.index).index(user_id)
        
        # Ratings del usuario actual
        user_ratings = self.user_item_matrix.iloc[user_idx]
        watched_animes = user_ratings[user_ratings > 0].index.tolist()
        
        # Calcular similitud manualmente usando correlación de Pearson
        user_similarities = []
        for i in range(len(self.user_item_matrix)):
            if i == user_idx:
                user_similarities.append(0)  # No comparar consigo mismo
            else:
                # Calcular correlación entre usuarios
                corr = np.corrcoef(user_ratings, self.user_item_matrix.iloc[i])[0, 1]
                user_similarities.append(corr if not np.isnan(corr) else 0)
        
        user_similarities = np.array(user_similarities)
        
        # Promedio ponderado de ratings
        similar_users_ratings = self.user_item_matrix.values.T * user_similarities
        weighted_sum = similar_users_ratings.sum(axis=1)
        similarity_sum = np.abs(user_similarities).sum()
        
        # Evitar división por cero
        if similarity_sum < 1e-8:
            # Si no hay similitudes, recomendar animes populares
            return self._get_popular_recommendations(n_recommendations, exclude_animes=watched_animes)
        
        recommendation_scores = weighted_sum / similarity_sum
        
        # Crear DataFrame con resultados
        anime_scores = pd.DataFrame({
            'anime_id': self.user_item_matrix.columns,
            'score': recommendation_scores
        })
        
        # Filtrar animes que el usuario ya ha visto
        anime_scores = anime_scores[~anime_scores['anime_id'].isin(watched_animes)]
        
        # Ordenar por score y tomar los mejores
        top_recommendations = anime_scores.nlargest(n_recommendations, 'score')
        
        # Formatear resultados
        recommendations = []
        for _, row in top_recommendations.iterrows():
            anime_id = row['anime_id']
            anime_info = self.anime_df[self.anime_df['anime_id'] == anime_id]
            
            if not anime_info.empty:
                anime_data = anime_info.iloc[0]
                recommendations.append({
                    'anime_id': int(anime_id),
                    'title': anime_data.get('name', 'Desconocido'),
                    'genre': anime_data.get('genre', 'Desconocido'),
                    'type': anime_data.get('type', 'Desconocido'),
                    'recommendation_score': round(float(row['score']), 4)
                })
        
        return recommendations
    
    def _get_popular_recommendations(self, n_recommendations=10, exclude_animes=None):
        """Método de respaldo: recomendar animes populares basados en rating promedio"""
        if exclude_animes is None:
            exclude_animes = []
        
        # Calcular rating promedio por anime
        anime_avg_ratings = self.ratings_df.groupby('anime_id')['rating'].mean().reset_index()
        anime_avg_ratings.columns = ['anime_id', 'avg_rating']
        
        # Combinar con información del anime
        popular_animes = anime_avg_ratings.merge(
            self.anime_df[['anime_id', 'name', 'genre', 'type']], 
            on='anime_id', 
            how='left'
        )
        
        # Filtrar animes excluidos
        popular_animes = popular_animes[~popular_animes['anime_id'].isin(exclude_animes)]
        
        # Ordenar por rating promedio y tomar los mejores
        popular_animes = popular_animes.nlargest(n_recommendations, 'avg_rating')
        
        # Formatear resultados
        recommendations = []
        for _, row in popular_animes.iterrows():
            recommendations.append({
                'anime_id': int(row['anime_id']),
                'title': row.get('name', 'Desconocido'),
                'genre': row.get('genre', 'Desconocido'),
                'type': row.get('type', 'Desconocido'),
                'recommendation_score': round(float(row['avg_rating']), 4),
                'note': 'Recomendación popular (fallback)'
            })
        
        return recommendations