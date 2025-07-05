from flask import Flask, request, jsonify
import requests
import os
import logging

app = Flask(__name__)

# Setup logging to ensure logs appear in Render
logging.basicConfig(level=logging.INFO)

@app.route('/', methods=['POST'])
def index():
    data = request.get_json()
    logging.info(f"DEBUG PAYLOAD: {data}")  # Logs request data to Render

    # Get parameters safely
    unit = data['queryResult']['parameters'].get('unit-currency3')
    target_list = data['queryResult']['parameters'].get('currency-name3')

    # Validate parameters
    if not unit or not target_list:
        logging.warning("Missing parameters in request.")
        return jsonify({'fulfillmentText': "Sorry, I couldn't understand your currency request."})

    source_currency = unit.get('currency')
    amount = unit.get('amount')
    target_currency = target_list[0] if isinstance(target_list, list) else target_list

    if not source_currency or not amount or not target_currency:
        logging.warning("Incomplete currency data received.")
        return jsonify({'fulfillmentText': "Missing currency or amount information."})

    try:
        # Get conversion rate
        cf = fetch_conversion_factor(source_currency, target_currency)
        final_amount = round(amount * cf, 2)

        reply = f"{amount} {source_currency} is {final_amount} {target_currency}"
        logging.info(f"Replying with: {reply}")

        return jsonify({'fulfillmentText': reply})

    except Exception as e:
        logging.error(f"Conversion failed: {e}")
        return jsonify({'fulfillmentText': "There was an error while fetching the conversion rate."})

# Optional GET route for browser check
@app.route('/', methods=['GET'])
def home():
    return "Currency Converter Bot is live!"

# Fetch conversion rate from external API
def fetch_conversion_factor(source, target):
    api_key = "cur_live_hwd5a6BO9VN6QUcxbSYacQnNxvLQVkuPNg4YPmBy"
    url = f"https://api.currencyapi.com/v3/latest?apikey={api_key}&base_currency={source}&currencies={target}"

    response = requests.get(url)
    response.raise_for_status()  # Will raise an exception for HTTP errors
    data = response.json()

    return data['data'][target]['value']

# Required for Render to use correct port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
