import sys
import os
from flask import Flask, request, jsonify
from pyzill.details import get_from_home_url  # Direct property lookup

app = Flask(__name__)

@app.route("/scrape", methods=["GET"])
def scrape_zillow():
    address = request.args.get("address")

    if not address:
        return jsonify({"error": "No address provided"}), 400

    try:
        # Convert the address into a Zillow search URL
        zillow_url = f"https://www.zillow.com/homes/{address.replace(' ', '-')}/"

        # Fetch listing details from Zillow
        property_data = get_from_home_url(zillow_url)

        if not property_data:
            return jsonify({"error": "No data found for this address"}), 404

        # Extract useful details
        data = {
            "zpid": property_data.get("zpid"),
            "price_history": property_data.get("priceHistory", []),
            "zestimate": property_data.get("zestimate", "N/A"),
            "status": property_data.get("homeStatus", "Unknown"),
            "zillow_url": zillow_url
        }

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
