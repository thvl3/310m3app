import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import boto3

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Connect to DynamoDB
dynamodb = boto3.resource("dynamodb", region_name="us-west-1")
table = dynamodb.Table("RestaurantQuiz")

@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing request body"}), 400

        # Normalize user input
        user_prefs = {
            "cuisine": data.get("cuisine", "").strip().lower(),
            "budget": data.get("budget", "").strip(),
            "vibe": data.get("vibe", "").strip().lower(),
            "social": data.get("social", "").strip().lower(),
            "dietary": data.get("dietary", "").strip().lower(),
            "group_size": data.get("group_size", "").strip().lower(),
            "service_speed": data.get("service_speed", "").strip().lower()
        }

        # Fetch all restaurants
        response = table.scan()
        restaurants = response.get("Items", [])

        best_match = None
        highest_score = 0

        for restaurant in restaurants:
            score = 0

            if restaurant.get("Cuisine_Type", "").strip().lower() == user_prefs["cuisine"]:
                score += 7

            if user_prefs["budget"] in restaurant.get("Price_Level", ""):
                score += 3

            if user_prefs["vibe"] in restaurant.get("Vibe", "").strip().lower():
                score += 2

            if user_prefs["social"] in restaurant.get("Social_Interaction_Level", "").strip().lower():
                score += 2

            if user_prefs["dietary"] in restaurant.get("ETC", "").strip().lower():
                score += 4

            if user_prefs["group_size"] in restaurant.get("Group_Size", "").strip().lower():
                score += 2

            if user_prefs["service_speed"] in restaurant.get("Service_Speed", "").strip().lower():
                score += 2

            if score > highest_score:
                highest_score = score
                best_match = restaurant.get("Restaurant_ID", "no_match")

        # Generate image URL
        image_path = f"/static/images/{best_match}.png"
        if not os.path.exists(os.path.join("static/images", f"{best_match}.png")):
            image_path = "/static/images/default.png"  # Fallback to default

        return jsonify({"restaurant": best_match, "image_url": image_path})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Serve static images
@app.route("/static/images/<filename>")
def serve_image(filename):
    return send_from_directory("static/images", filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
