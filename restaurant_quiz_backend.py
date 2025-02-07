from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Temporary restaurant data (Replace with DynamoDB later)
restaurants = [
    {"name": "Burger Joint", "cuisine": "american", "budget": "$", "atmosphere": "casual"},
    {"name": "Fancy Pasta", "cuisine": "italian", "budget": "$$$", "atmosphere": "romantic"},
    {"name": "Sushi Spot", "cuisine": "asian", "budget": "$$", "atmosphere": "lively"},
    {"name": "Taco Haven", "cuisine": "mexican", "budget": "$", "atmosphere": "casual"}
]

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    
    # Find the best match (Simple filtering for now)
    best_match = None
    for restaurant in restaurants:
        if (restaurant["cuisine"] == data.get("cuisine") and
            restaurant["budget"] == data.get("budget") and
            restaurant["atmosphere"] == data.get("atmosphere")):
            best_match = restaurant
            break
    
    return jsonify({"restaurant": best_match["name"] if best_match else "No match found"})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")  # Ensure Flask listens for external connections
