"""main.py for exposing endpoint(s)"""

import os
import subprocess
import json
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from adapters.redis_adapter import RedisAdapter
from csv_to_redis_loader import CsvToRedisLoader

app = Flask(__name__, template_folder="../templates")
app.secret_key = (
    "\xf8\x11)\x18\xc0\x0f\xa0\xd9\x1f\x10\xbcW12\xc2\xbf\t\x9b\xa6\\}\x90>"
)


# only use Redis when needed (for fetching data)
def get_redis_connection():
    """return Redis adapter"""
    return RedisAdapter(host="redis", logger=app.logger)


def load_csv_to_redis():
    """set up Loader class to handle redis import"""
    CsvToRedisLoader(
        redis_adapter=get_redis_connection(),
        csv_file="/app/output/hospitals_and_procedures.csv",
        log=app.logger,
    )


@app.route("/")
def index():
    """root"""
    try:
        return jsonify({"message": "Welcome to the Hospital API"})
    except Exception as e:
        app.logger.error("Failed to load the root endpoint: %s", e)
        return jsonify({"error": "Unable to load the homepage."}), 500


@app.route("/api/generate_csv", methods=["POST"])
def generate_csv():
    """generate csv"""
    try:
        script_path = os.path.join(
            os.path.dirname(__file__), "generate_hospitals_csv.py"
        )
        subprocess.run(["python", script_path], check=True)
        flash("CSV file generated successfully!")
    except subprocess.CalledProcessError as e:
        app.logger.error("Could not generate CSV: %s", str(e))
        flash("An error occurred while generating the CSV file.")

    # return valid http response
    return redirect(url_for("manage_hospitals"))


@app.route("/api/hospitals/manage", methods=["GET", "POST"])
def manage_hospitals():
    """manage Redis data on frontend"""
    r = get_redis_connection()
    if request.method == "POST":
        # delete, then reload
        r.delete_all_keys()
        load_csv_to_redis()
        return redirect(url_for("manage_hospitals"))

    hospital_keys = r.keys("hospital:*")
    hospital_count = len(hospital_keys)

    return render_template("manage_hospitals.html", hospital_count=hospital_count)


@app.route("/api/hospitals/<hospital_id>", methods=["GET"])
def get_hospital(hospital_id):
    """get hospital data using hsospital_id"""
    r = get_redis_connection()
    hospital = r.get(f"hospital:{hospital_id}")
    if hospital:
        app.logger.debug(
            "Returned hospital ID %s and its associated procedures.", hospital_id
        )
        return jsonify(json.loads(hospital))
    app.logger.error("Error retrieving hospital ID %s", hospital_id)
    return jsonify({"error": "Hospital not found"}), 404


if __name__ == "__main__":
    # setting host="0.0.0.0" is required for access outside container
    app.run(debug=True, host="0.0.0.0")
