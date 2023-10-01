from flask import Flask, render_template, request, jsonify
import os
from google.cloud import dialogflow

# Initialize Flask app with a static folder for storing audio files
app = Flask(__name__, static_folder='static')

# Set Google Application credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-credentials.json"

# Route to serve the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle detecting intent from user input
@app.route("/detect-intent", methods=["POST"])
def detect_intent():
    """Returns the detected intent for a given utterance."""
    # Get user input from request JSON
    utterance = request.json['text']

    # Initialize Dialogflow session client
    session_client = dialogflow.SessionsClient()
    session_id = "5e6e1df3-fafb-481f-8f74-b81241ccb015"
    project_id = "ba-test-qeps"

    # Create text input with given utterance and language code
    text_input = dialogflow.TextInput(text=utterance, language_code="de-DE")
    query_input = dialogflow.QueryInput(text=text_input)

    # Configure the output audio settings for Dialogflow
    output_audio_config = dialogflow.OutputAudioConfig(
        audio_encoding=dialogflow.OutputAudioEncoding.OUTPUT_AUDIO_ENCODING_LINEAR_16,
        synthesize_speech_config=dialogflow.SynthesizeSpeechConfig(
            speaking_rate=1.05,
            voice=dialogflow.VoiceSelectionParams(
                name='de-DE-Wavenet-B'
            ))
    )

    # Create a session path and send the detect intent request
    session = session_client.session_path(project_id, session_id)
    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input, "output_audio_config": output_audio_config})

    # Extract necessary information from the response
    fulfillment_messages = response.query_result.fulfillment_messages

    # Concatenate text from fulfillment messages
    concatenated_text = " ".join([i.text.text.pop() for i in fulfillment_messages])

    # Save the output audio to a file
    with open("static/output.wav", "wb") as out:
        out.write(response.output_audio)
        print('Audio content written to file "output.wav"')

    # Return the concatenated text as JSON
    return jsonify(result=concatenated_text)

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0")
