from flask import Flask, render_template, request
import pandas as pd
import networkx as nx


app = Flask(__name__)

# Code For Logical Part

def recommend_movies(user_id, preferred_genre):
    movies = pd.read_csv("movies.csv")
    ratings = pd.read_csv("ratings.csv")

    # Mergeing both datasets
    data = pd.merge(ratings, movies, on="movieid")

    # Filtering movies with rating >= 3
    filtered = data[data["rating"] >= 3]

    # Building weighted bipartite graph
    G = nx.Graph()
    for row in filtered.itertuples():
        user = f"U{row.userid}"
        movie = row.title
        rating = row.rating
        G.add_edge(user, movie, weight=rating)

    # Movies already seen by the targeted user
    seen_movies = set(data[data["userid"] == user_id]["title"])

    # Finding connected users
    connected_users = set()
    for movie in seen_movies:
    # Skips if movie not in graph
        if movie not in G: 
            continue
        for neighbor in G.neighbors(movie):
            if neighbor != f"U{user_id}" and neighbor.startswith("U"):
                connected_users.add(neighbor)


    # Weighted recommendations
    recommendation_scores = {}
    for user in connected_users:
        for movie in G.neighbors(user):
            if movie not in seen_movies:
                edge_weight = G[user][movie]['weight']
                recommendation_scores[movie] = recommendation_scores.get(movie, 0) + edge_weight

    # Filtering by chosen genre (supports multiple genres)
    genre_filtered = movies[movies["title"].isin(recommendation_scores.keys())]
    genre_filtered = genre_filtered[genre_filtered["genre"].str.lower().str.contains(preferred_genre.lower())]

    if genre_filtered.empty:
        return []

    # Returning sorted list of recommended movies
    recommendations = sorted(
        [(movie, recommendation_scores[movie]) for movie in genre_filtered["title"]],
        key=lambda x: x[1],
        reverse=True
    )
    return recommendations

#---------------------
# Flask Routes
#---------------------

# Linking html with python code with Flask
@app.route('/')
def home():
    return render_template('index.html', recommendations=None)


# Recommending Movies Based on User Input
@app.route('/recommend', methods=['POST'])
def recommend():
    user_id = int(request.form['user_id'])
    genre = request.form['genre']
    recommendations = recommend_movies(user_id, genre)
    return render_template('index.html', recommendations=recommendations, user_id=user_id, genre=genre)

if __name__ == "__main__":
    app.run(debug=True)
