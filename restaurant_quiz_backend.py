import boto3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configure AWS DynamoDB
dynamodb = boto3.resource("dynamodb", region_name="us-west-2")  # Change to your AWS region
table = dynamodb.Table("Restaurants")

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    
    # Query restaurants based on user preferences
    response = table.scan()  # Fetch all data (consider using filters in production)
    restaurants = response.get("Items", [])

    best_match = None
    for restaurant in restaurants:
        if (restaurant["cuisine"] == data.get("cuisine") and
            restaurant["budget"] == data.get("budget") and
            restaurant["atmosphere"] == data.get("atmosphere")):
            best_match = restaurant
            break
    
    return jsonify({"restaurant": best_match["name"] if best_match else "No match found"})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
