from flask import Flask, render_template, request, jsonify
from authlib.integrations.flask_client import OAuth
import os
import google.generativeai as genai
from google.generativeai.types import generation_types

app = Flask(__name__)
app.secret_key =os.getenv('','')

oauth=OAuth(app)
oauth.register(
    name='google',
    client_id='',
    client_secret='',
    access_token_url=''
    authorize_url=''
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope':'openid email profile'},
)

# Configure the AI API key and model name
api_key = "AIzaSyCQJhlKJEfgCH3kBYsOssnvAS9fs7VJxSY"
model_name = "gemini-1.0-pro"
genai.configure(api_key=api_key)

# Initialize the Generative AI model
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048
}
safety_settings = [
    # ... safety settings (same as before)
]
model = genai.GenerativeModel(model_name=model_name,
                              generation_config=generation_config,
                              safety_settings=safety_settings)

conversation_history = []  # Initialize conversation history
bot_initialized = False  # Flag to track bot initialization

def initialize_bot():
    global bot_initialized
    if not bot_initialized:
        bot_initialized = True
        init_response = "Hello I am Dr. Serenity Mindwel. Welcome to the realm of tranquility. How may I assist you on your journey to inner harmony?"
        conversation_history.append({"role": "ChatBot", "text": init_response})
        return init_response
    else:
        return None

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/chatbot")
def chatbot():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form["user_input"]

    # Initialize the bot if not already initialized
    init_response = initialize_bot()
    if init_response:
        return jsonify({"response": init_response, "role": "ChatBot"})

    # Add user input to conversation history
    conversation_history.append({"role": "User", "text": user_input})

    # Construct input for the model
    input_text = "\n".join(f"{entry['role']}: {entry['text']}" for entry in conversation_history)

    # Provide input to the model
    response = model.generate_content(input_text)

    # Extract bot's response
    generated_content = response._result.candidates[0].content.parts[0].text

    # Add bot's response to conversation history without prefix
    conversation_history.append({"role": "ChatBot", "text": generated_content})

    # Remove the prefix from the response
    if generated_content.startswith("ChatBot: "):
        generated_content = generated_content.replace("ChatBot:", "")

    return jsonify({"response": generated_content, "role": "ChatBot"})

if __name__ == "__main__":
    app.run(debug=True)