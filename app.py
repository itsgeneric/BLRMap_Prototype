from flask import Flask, render_template
import os
from dotenv import load_dotenv

# Initialize Flask app
app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


@app.route("/")
def home():
    """
    Serves the main routing hub interface.
    Passes the API key to the frontend so it isn't hardcoded.
    """
    if not API_KEY:
        return "Error: GOOGLE_MAPS_API_KEY is missing from the .env file.", 500

    return render_template("index.html", api_key=API_KEY)


if __name__ == "__main__":
    # Run the app locally on port 5000
    app.run(debug=True, port=5000)