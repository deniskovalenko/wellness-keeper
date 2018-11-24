from flask import Flask, request, jsonify
from google.cloud import bigquery

app = Flask(__name__)
client = bigquery.Client()
dataset_id = 'heart_rate'
table_id = 'heart_rate_bpm'
table_ref = client.dataset(dataset_id).table(table_id)
table = client.get_table(table_ref)


@app.route('/bpm', methods=['POST'])
def main():
    content = request.json

    user_id = content["user_id"]
    bpm = content["bpm"]
    email = content["email"]
    user_event_timestamp = content["timestamp"]
    aggregated_for = content["aggregated_for"]

    row_to_insert = [
        (user_id, email, bpm, user_event_timestamp, aggregated_for)
    ]

    errors = client.insert_rows(table, row_to_insert)
    return jsonify({"result": "ok", "erros": errors})


if __name__ == '__main__':
    app.run(debug=True)
# [END gae_python37_bigquery]