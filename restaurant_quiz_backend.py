import boto3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Connect to DynamoDB without explicit AWS credentials
dynamodb = boto3.resource("dynamodb", region_name="us-west-2")  # Change to your AWS region
table = dynamodb.Table("Restaurants")

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
    app.run(debug=True, host="0.0.0.0")
