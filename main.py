import flask
from flask import Flask, request, make_response, jsonify
import requests
import json
from datetime import datetime

# Initialize the Flask app
app = Flask(__name__)

# API endpoint for order status
api = "https://orderstatusapi-dot-organization-project-311520.uc.r.appspot.com/api/getOrderStatus"

# Downloaded Postman collection (if applicable)
f = open("OrderStatusAPI.json")
orderstatus_json = json.load(f)



def results():
    # Build a request object
    req = request.get_json(force=True)

    # Check if order_id is present in the request
    if not req or not req.get('queryResult') or not req['queryResult'].get('parameters') or not req['queryResult']['parameters'].get('order_id'):
        return {'fulfillmentText': 'Sorry, I couldn\'t find an order ID in your request. Please provide a valid order ID to check the shipment date.'}

    # Fetch order ID
    order_id = req.get('queryResult').get('parameters')['order_id']

    # Make a POST request to retrieve shipment date
    try:
        response = requests.post(url=api, json=orderstatus_json, data={"orderId": str(order_id)}).json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request to order status API: {e}")
        return {'fulfillmentText': 'There was an error checking your order status. Please try again later.'}

    # Extract and format shipment date (assuming the response structure remains the same)
    if response.get('error'):
        return {'fulfillmentText': response['error']}  # Handle API error message

    shipment_date = response.get('shipmentDate')
    if shipment_date:
        try:
            #Converting Shipment date to ISO 8601
            shipment_date_obj = datetime.strptime(shipment_date, "%Y-%m-%dT%H:%M:%S.%fZ")
            formatted_date = shipment_date_obj.strftime("%A, %d %b %Y")
            return {'fulfillmentText': f'Your order {order_id} will be shipped on {formatted_date}.'}
        except ValueError:
            return {'fulfillmentText': 'Invalid shipment date received.'}
    else:
        return {'fulfillmentText': f'Shipment information not found for order {order_id}.'}  # Handle missing shipment date

# Webhook route
@app.route('/webhook', methods=['GET','POST'])

def webhook():
    # Return response
    return make_response(jsonify(results()))

# Run the app
#if __name__ == '__main__':
#   app.run()
