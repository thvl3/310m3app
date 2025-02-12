from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import boto3

app = Flask(__name__, template_folder="templates")
CORS(app)

# Connect to DynamoDB
dynamodb = boto3.resource("dynamodb", region_name="us-west-1")
table = dynamodb.Table("Restaurants")  # Update with your actual table name

# Assign weight importance
WEIGHTS = {
    "cuisine": 4,
    "budget": 3,
    "vibe": 2,
    "social": 2,
    "dietary": 5
}

def map_budget(budget):
    """Convert budget symbols to DynamoDB values"""
    BUDGET_MAP = {
        "$": "1-10",
        "$$": "10-20",
        "$$$": "20-30",
        "$$$$": "30+"
    }
    return BUDGET_MAP.get(budget, budget)

@app.route("/", methods=["GET"])
def home():
    """ Serve the quiz page """
    return render_template("index.html")

@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing request body"}), 400

        # Normalize user input
        user_prefs = {
            "cuisine": data.get("cuisine", "").strip().lower(),
            "budget": map_budget(data.get("budget", "").strip()),
            "vibe": data.get("vibe", "").strip().lower(),
            "social": data.get("social", "").strip().lower(),
            "dietary": data.get("dietary", "").strip().lower()
        }

        # Fetch all restaurants
        response = table.scan()
        restaurants = response.get("Items", [])

        best_match = None
        highest_score = 0

        for restaurant in restaurants:
            score = 0

            # Match Cuisine (highest weight)
            if restaurant.get("Cuisine_Type", "").strip().lower() == user_prefs["cuisine"]:
                score += WEIGHTS["cuisine"]

            # Match Budget
            if user_prefs["budget"] in restaurant.get("Price_Level", ""):
                score += WEIGHTS["budget"]

            # Match Vibe
            if user_prefs["vibe"] in restaurant.get("Vibe", "").strip().lower():
                score += WEIGHTS["vibe"]

            # Match Social Level
            if user_prefs["social"] in restaurant.get("Social_Interaction_Level", "").strip().lower():
                score += WEIGHTS["social"]

            # Match Dietary Preferences (optional)
            if user_prefs["dietary"] in restaurant.get("ETC", "").strip().lower():
                score += WEIGHTS["dietary"]

            # Track best match
            if score > highest_score:
                highest_score = score
                best_match = restaurant.get("Restaurant_ID", "No match found")

        return jsonify({"restaurant": best_match})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
