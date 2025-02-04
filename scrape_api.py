import sys
import os

# Ensure Python can find the `src/` directory
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Now import pyzill
import pyzill
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/scrape", methods=["GET"])
def scrape_zillow():
    address = request.args.get("address")

    if not address:
        return jsonify({"error": "No address provided"}), 400

    try:
        results = pyzill.for_sale(1, address)

        if results and "properties" in results:
            property_data = results["properties"][0]
            data = {
                "zpid": property_data.get("zpid"),
                "price_history": property_data.get("priceHistory", []),
                "zestimate": property_data.get("zestimate", "N/A"),
                "status": property_data.get("homeStatus", "Unknown"),
            }
            return jsonify(data)

        return jsonify({"error": "No data found for this address"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
