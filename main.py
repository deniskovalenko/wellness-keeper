from flask import Flask, request, jsonify
from google.cloud import bigquery
from google.cloud import texttospeech
import requests
import os
from requests.auth import HTTPBasicAuth

app = Flask(__name__)
bigquery_client = bigquery.Client()
dataset_id = 'heart_rate'
table_id = 'bpm'
table_ref = bigquery_client.dataset(dataset_id).table(table_id)
table = bigquery_client.get_table(table_ref)
events_table_id = 'event'
events_table_ref = bigquery_client.dataset(dataset_id).table(events_table_id)
events_table = bigquery_client.get_table(events_table_ref)
client = texttospeech.TextToSpeechClient()

basicAuth = HTTPBasicAuth(os.environ.get('46_ELKS_USERNAME'), os.environ.get('46_ELKS_PASSWORD'))


@app.route('/bpm', methods=['POST'])
def collect_hear_rate():
    content = request.get_json()

    user_id = content["user_id"]
    bpm = content["bpm"]
    email = content["email"]
    timestamp = content["timestamp"]
    aggregated_for = content["aggregated_for"]

    row_to_insert = [
        (user_id, bpm, email, timestamp, aggregated_for)
    ]

    errors = bigquery_client.insert_rows(table, row_to_insert)
    return jsonify({"result": "ok", "errors": errors})



@app.route('/userEvent', methods=['POST'])
def collect_user_event():
    content = request.get_json(force=True)

    user_id = content["user_id"]
    event = content["event"]
    timestamp = content["timestamp"]

    row_to_insert = [
        (user_id, event, timestamp)
    ]

    errors = bigquery_client.insert_rows(events_table, row_to_insert)
    return jsonify({"result": "ok", "errors": errors})


@app.route('/callEmergency', methods=['POST'])
def emergency_call():
    json = request.get_json(force=True)
    from_phone_number = json["from_phone_number"]
    to_phone_number = json["to_phone_number"]
    message = json["message"]
    send_sms = json["send_sms"]

    if (send_sms==1):
        print('sending sms to ' + to_phone_number)
        requestBody = {"from": from_phone_number, "to": to_phone_number, "message": message}
        requests.post("https://api.46elks.com/a1/sms", json=requestBody, auth=basicAuth)
        # todo send sms as well
    print(f'calling with message {message}')

    mp3_uri = synthesize_voice(message)
    print(mp3_uri)
    action = '{"play": ' + '"' + mp3_uri + '"}'
    requestBody = {"from": from_phone_number, "to": to_phone_number, "voice_start": action}
    response = requests.post("https://api.46elks.com/a1/calls",
                             json=requestBody, auth=basicAuth)

    return jsonify({"result": "ok", "status": response.status_code})


def synthesize_voice(message):
    synthesis_input = texttospeech.types.SynthesisInput(text=message)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.types.VoiceSelectionParams(
        language_code='en-US',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)

    # Select the type of audio file you want returned
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(synthesis_input, voice, audio_config)
    result = requests.post('https://file.io', files=dict(file=("call.mp3", response.audio_content)))

    return result.json()["link"]


if __name__ == '__main__':
    app.run(debug=True)
# [END gae_python37_bigquery]
