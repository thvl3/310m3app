from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Connect to DynamoDB
dynamodb = boto3.resource("dynamodb", region_name="us-west-1")
table = dynamodb.Table("Restaurants")  # Ensure this matches your table name

# Convert user-friendly budget to price range stored in DynamoDB
BUDGET_MAP = {
    "$": "1-10",
    "$$": "10-20",
    "$$$": "20-30",
    "$$$$": "30+"
}

def map_budget(budget):
    return BUDGET_MAP.get(budget, budget)  # Default to input if no match

@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        data = request.get_json()
        if not all(k in data for k in ["cuisine", "budget", "atmosphere"]):
            return jsonify({"error": "Missing required parameters"}), 400

        # Normalize input
        cuisine = data["cuisine"].strip().lower()
        budget = map_budget(data["budget"].strip())
        atmosphere = data["atmosphere"].strip().lower()
        social_interaction = data.get("social_interaction", "").strip().lower()  # Optional
        etc = data.get("etc", "").strip().lower()  # Additional filters like vegan, gluten-free

        # Scan DynamoDB for all restaurants
        response = table.scan()
        restaurants = response.get("Items", [])

        # Filtering logic
        recommendations = []
        for r in restaurants:
            if r.get("Cuisine_Type", "").strip().lower() != cuisine:
                continue  # Skip if cuisine doesn't match
            
            if budget not in r.get("Price_Level", ""):
                continue  # Skip if budget doesn't match
            
            if atmosphere and atmosphere not in r.get("Vibe", "").strip().lower():
                continue  # Skip if vibe doesn't match

            if social_interaction and social_interaction not in r.get("Social_Interaction_Level", "").strip().lower():
                continue  # Skip if social interaction preference doesn't match

            if etc and etc not in r.get("ETC", "").strip().lower():
                continue  # Skip if additional filters don't match
            
            recommendations.append({
                "name": r.get("Restaurant_ID", "Unknown"),
                "cuisine": r.get("Cuisine_Type", ""),
                "price": r.get("Price_Level", ""),
                "vibe": r.get("Vibe", ""),
                "social": r.get("Social_Interaction_Level", ""),
                "etc": r.get("ETC", ""),
            })

        return jsonify({"recommendations": recommendations})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "<h1>Welcome to the Restaurant Quiz</h1><p>Use the /recommend endpoint to get suggestions.</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
