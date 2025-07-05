from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    data = request.get_json()
    print("DEBUG PAYLOAD:", data,flush=True)  # For checking Dialogflow request in Render logs

    # Safely extract parameters from Dialogflow
    unit = data['queryResult']['parameters'].get('unit-currency3')
    target_list = data['queryResult']['parameters'].get('currency-name3')

    # Validate parameters
    if not unit or not target_list:
        return jsonify({'fulfillmentText': "Sorry, I couldn't understand the currency conversion request."})

    source_currency = unit.get('currency')
    amount = unit.get('amount')
    target_currency = target_list[0] if isinstance(target_list, list) else target_list

    # Validate extracted values
    if not source_currency or not amount or not target_currency:
        return jsonify({'fulfillmentText': "Missing currency or amount information."})

    try:
        # Fetch conversion rate
        cf = fetch_conversion_factor(source_currency, target_currency)
        final_amount = round(amount * cf, 2)

        response = {
            'fulfillmentText': f"{amount} {source_currency} is {final_amount} {target_currency}"
        }
    except Exception as e:
        print("ERROR:", str(e))
        response = {
            'fulfillmentText': "Something went wrong while fetching the exchange rate."
        }

    return jsonify(response)

@app.route('/', methods=['GET'])  # Optional: health check
def home():
    return "Currency Converter Bot is live!"

def fetch_conversion_factor(source, target):
    api_key = "cur_live_hwd5a6BO9VN6QUcxbSYacQnNxvLQVkuPNg4YPmBy"  # You can move this to env variable
    url = f"https://api.currencyapi.com/v3/latest?apikey={api_key}&base_currency={source}&currencies={target}"
    
    response = requests.get(url)
    response.raise_for_status()  # Raises HTTPError for bad responses (4xx, 5xx)
    data = response.json()

    return data['data'][target]['value']

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Required for Render deployment
    app.run(host='0.0.0.0', port=port)
