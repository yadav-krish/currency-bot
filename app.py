from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    data = request.get_json()

    source_currency = data['queryResult']['parameters']['unit-currency3']['currency']
    amount = data['queryResult']['parameters']['unit-currency3']['amount']
    target_currency = data['queryResult']['parameters']['currency-name3'][0]

    cf = fetch_conversion_factor(source_currency, target_currency)
    final_amount = amount * cf
    final_amount = round(final_amount, 2)

    response = {
        'fulfillmentText': "{} {} is {} {}".format(amount, source_currency, final_amount, target_currency)
    }
    return jsonify(response)

def fetch_conversion_factor(source, target):
    url = f"https://api.currencyapi.com/v3/latest?apikey=cur_live_hwd5a6BO9VN6QUcxbSYacQnNxvLQVkuPNg4YPmBy&base_currency={source}&currencies={target}"
    response = requests.get(url)
    response = response.json()

    return response['data'][target]['value']

if __name__ == "__main__":
    app.run(debug=True)
