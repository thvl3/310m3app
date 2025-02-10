import boto3
from flask import Flask, request, jsonify

app = Flask(__name__)

# Enable CORS for cross-origin requests
from flask_cors import CORS
CORS(app)

# Connect to DynamoDB
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")  # Change to your AWS region
table = dynamodb.Table("Restaurants")

@app.route('/')  # 👈 Add this route
def home():
    return "<h1>Welcome to the Restaurant Quiz</h1><p>Use the /recommend endpoint to get suggestions.</p>"

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    
    # Scan entire table (since filtering on Scan is limited)
    response = table.scan()
    restaurants = response.get("Items", [])

    # Find the best match
    best_match = None
    for restaurant in restaurants:
        if (restaurant["cuisine"] == data.get("cuisine") and
            restaurant["budget"] == data.get("budget") and
            restaurant["atmosphere"] == data.get("atmosphere")):
            best_match = restaurant
            break
    
    return jsonify({"restaurant": best_match["name"] if best_match else "No match found"})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=80)
