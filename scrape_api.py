import sys
import os
import random
import requests

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

# Proxy List (Webshare)
PROXY_LIST = [
    "http://jmskfoff:4w2hn50bhi2x@198.23.239.134:6540",
    "http://jmskfoff:4w2hn50bhi2x@207.244.217.165:6712",
    "http://jmskfoff:4w2hn50bhi2x@107.172.163.27:6543",
    "http://jmskfoff:4w2hn50bhi2x@64.137.42.112:5157",
    "http://jmskfoff:4w2hn50bhi2x@173.211.0.148:6641"
]

# Headers to mimic a real user
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    "DNT": "1",
    "Connection": "keep-alive"
}

def get_random_proxy():
    """Select a random proxy from the list and return it in the proper format"""
    proxy = random.choice(PROXY_LIST)
    return {"http": proxy, "https": proxy}


@app.route("/scrape", methods=["GET"])
def scrape_zillow():
    address = request.args.get("address")

    if not address:
        return jsonify({"error": "No address provided"}), 400

    try:
        zillow_url = f"https://www.zillow.com/homes/{address.replace(' ', '-')}/"

        app.logger.debug(f"Fetching data from: {zillow_url}")

        # Try up to 3 times with different proxies
        for attempt in range(3):
            proxy = get_random_proxy()
            app.logger.debug(f"Using Proxy: {proxy}")

            try:
                # Send the request with a random proxy
                response = requests.get(zillow_url, headers=HEADERS, proxies=proxy, timeout=10)

                if response.status_code == 403:
                    app.logger.warning(f"Proxy blocked (403). Retrying... [{attempt+1}/3]")
                    continue  # Try another proxy

                if response.status_code != 200:
                    app.logger.error(f"Request failed with status {response.status_code}")
                    return jsonify({"error": f"Request failed. Status code: {response.status_code}"}), response.status_code

                # Fetch property details
                property_data = get_from_home_url(zillow_url)

                if not property_data:
                    app.logger.error(f"No data found for address: {address}")
                    return jsonify({"error": "No data found for this address"}), 404

                data = {
                    "zpid": property_data.get("zpid"),
                    "price_history": property_data.get("priceHistory", []),
                    "zestimate": property_data.get("zestimate", "N/A"),
                    "status": property_data.get("homeStatus", "Unknown"),
                    "zillow_url": zillow_url
                }

                app.logger.debug(f"Scraped Data: {data}")
                return jsonify(data)

            except requests.exceptions.RequestException as e:
                app.logger.warning(f"Request failed with {proxy}: {str(e)}")
                continue  # Try the next proxy

        return jsonify({"error": "All proxies blocked. Try again later."}), 403

    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
