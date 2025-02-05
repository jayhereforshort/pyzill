import sys
import os
# Ensure Python can find the `src/` directory
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import pyzill
import logging
from flask import Flask, request, jsonify
from pyzill.details import get_from_home_url  # Directly fetch listing details

# Initialize Flask app
app = Flask(__name__)

# Enable logging
logging.basicConfig(level=logging.DEBUG)

# Custom Headers (Mimic a real browser)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    "DNT": "1",
    "Connection": "keep-alive"
}

@app.route("/scrape", methods=["GET"])
def scrape_zillow():
    address = request.args.get("address")

    if not address:
        return jsonify({"error": "No address provided"}), 400

    try:
        zillow_url = f"https://www.zillow.com/homes/{address.replace(' ', '-')}/"

        # Log the request
        app.logger.debug(f"Fetching data from: {zillow_url}")

        # Fetch listing details from Zillow
        property_data = get_from_home_url(zillow_url)

        if not property_data:
            app.logger.error(f"No data found for address: {address}")
            return jsonify({"error": "No data found for this address"}), 404

        # Extract relevant details
        data = {
            "zpid": property_data.get("zpid"),
            "price_history": property_data.get("priceHistory", []),
            "zestimate": property_data.get("zestimate", "N/A"),
            "status": property_data.get("homeStatus", "Unknown"),
            "zillow_url": zillow_url
        }

        app.logger.debug(f"Scraped Data: {data}")
        return jsonify(data)

    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
