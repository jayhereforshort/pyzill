import sys
import os
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

# Webshare Rotating Proxy
PROXY = {
    "http": "http://jmskfoff-rotate:4w2hn50bhi2x@p.webshare.io:80",
    "https": "http://jmskfoff-rotate:4w2hn50bhi2x@p.webshare.io:80"
}

# Improved Headers (Real Chrome Request)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Connection": "keep-alive"
}

# Example Zillow Cookies (Replace with real ones)
COOKIES = {
    "zguid": "23|67aa3dd9-4332-4c42-b742-dfb456abcd12",
    "zgsession": "23|abc123xyz456",
    "JSESSIONID": "abcxyz123456"
}

@app.route("/scrape", methods=["GET"])
def scrape_zillow():
    address = request.args.get("address")

    if not address:
        return jsonify({"error": "No address provided"}), 400

    try:
        zillow_url = f"https://www.zillow.com/homes/{address.replace(' ', '-')}/"
        app.logger.debug(f"Fetching data from: {zillow_url}")

        # Make request using proxy, headers, and cookies
        response = requests.get(zillow_url, headers=HEADERS, cookies=COOKIES, proxies=PROXY, timeout=10)

        if response.status_code == 403:
            app.logger.error("Zillow blocked the request even with obfuscation (403 Forbidden).")
            return jsonify({"error": "Zillow blocked this request. Try again later."}), 403

        if response.status_code != 200:
            app.logger.error(f"Request failed with status {response.status_code}")
            return jsonify({"error": f"Request failed. Status code: {response.status_code}"}), response.status_code

        # Fetch listing details
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
        app.logger.error(f"Request failed: {str(e)}", exc_info=True)
        return jsonify({"error": f"Request failed: {str(e)}"}), 500

    except Exception as e:
        app.logger.error(f"General error occurred: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
