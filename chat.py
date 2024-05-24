# from flask import Flask, render_template, request, jsonify
# import json
# import random
# import torch
# import os
# from NeuralNet.model import NeuralNet
# from NeuralNet.utils import tokenize, stem, bag_of_words

# app = Flask(__name__, static_url_path='/static')

# def load_data_and_model():
#     # Load intents data from a JSON file
#     with open('NeuralNet\\dataset.json', 'r') as json_data:
#         intents = json.load(json_data)

#     # Load the pre-trained model and data
#     FILE = "NeuralNet\\data.pth"
#     data = torch.load(FILE)

#     input_size = data["input_size"]
#     hidden_size = data["hidden_size"]
#     output_size = data["output_size"]
#     all_words = data['all_words']
#     tags = data['tags']
#     model_state = data["model_state"]

#     device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

#     model = NeuralNet(input_size, hidden_size, output_size).to(device)
#     model.load_state_dict(model_state)
#     model.eval()

#     return intents, all_words, tags, model, device

# def chatbot_response(intents, all_words, tags, model, device, sentence):
#     sentence = tokenize(sentence)
#     X = bag_of_words(sentence, all_words)
#     X = X.reshape(1, X.shape[0])
#     X = torch.from_numpy(X).to(device)

#     output = model(X)
#     _, predicted = torch.max(output, dim=1)

#     tag = tags[predicted.item()]

#     probs = torch.softmax(output, dim=1)
#     prob = probs[0][predicted.item()]

#     if prob.item() > 0.75:
#         for intent in intents['intents']:
#             if tag == intent["tag"]:
#                 return f"{random.choice(intent['responses'])}"
#     else:
#         return f"I do not understand your query , Please tell me in detail."

# intents, all_words, tags, model, device = load_data_and_model()

# def run_chatbot(question):
#     sentence = question
#     response = chatbot_response(intents, all_words, tags, model, device, sentence)
#     return response

# # Route to render the index.html file
# @app.route('/')

# def index():
#     return render_template('base.html')

# # Route to handle POST requests for predicted response
# @app.route('/get_response', methods=['POST'])
# def get_response():
#     # Get the question from the request
#     question = request.json.get('question')
    
#     # Process the question (you can replace this with your AI model logic)
#     # For demonstration purposes, let's just return a simple response
#     # predicted_response = f"You asked: '{question}'. This is the predicted response."
#     predicted_response = run_chatbot(question)

#     # Return the predicted response as JSON
#     return ({'response': predicted_response})

# if __name__ == '__main__':
#     app.run(debug=True)
# # if __name__ == "__main__":
# #     port = int(os.environ.get("PORT", 5000))
# #     app.run(host='0.0.0.0', port=port)

from functools import wraps
import os
from flask import session
import torch
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, abort
import json
import random
from NeuralNet.model import NeuralNet
from NeuralNet.utils import tokenize, bag_of_words

app = Flask(__name__, static_url_path='/static')
# Set a secret key for the Flask application
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment configurations
DATASET_PATH = os.getenv('DATASET_PATH', 'NeuralNet/dataset.json')
MODEL_PATH = os.getenv('MODEL_PATH', 'NeuralNet/data.pth')

def load_data_and_model():
    try:
        with open(DATASET_PATH, 'r') as json_data:
            intents = json.load(json_data)
    except FileNotFoundError:
        logger.error("Error: dataset.json file not found.")
        intents = {"intents": []}  # Fallback or handle as necessary

    try:
        data = torch.load(MODEL_PATH)
    except FileNotFoundError:
        logger.error("Error: data.pth file not found.")
        data = None  # Fallback or handle as necessary

    if data:
        input_size = data["input_size"]
        hidden_size = data["hidden_size"]
        output_size = data["output_size"]
        all_words = data['all_words']
        tags = data['tags']
        model_state = data["model_state"]

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        model = NeuralNet(input_size, hidden_size, output_size).to(device)
        model.load_state_dict(model_state)
        model.eval()
    else:
        model, all_words, tags, device = None, [], [], torch.device('cpu')

    return intents, all_words, tags, model, device

def chatbot_response(sentence):
    intents, all_words, tags, model, device = load_data_and_model()

    if not model:
        return "Model not loaded. Please check the logs for errors."

    sentence = tokenize(sentence)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                return random.choice(intent['responses'])
    else:
        return "I do not understand your query. Please tell me in detail."

# Function to check if user is logged in
def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_function

def run_chatbot(question):
    response = chatbot_response(question)
    return response

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    question = request.json.get('question')
    if not question:
        abort(400, description="Invalid input")
    predicted_response = run_chatbot(question)
    return jsonify({'response': predicted_response})

@app.route('/admin')
@login_required
def admin():
    return render_template('admin.html')

@app.route('/update_response', methods=['POST'])
@login_required
def update_responses():
    intents, _, _, _, _ = load_data_and_model()
    updated_intents = intents.copy()
    for intent in updated_intents['intents']:
        new_response = request.form.get(f'response_{intent["tag"]}')
        if new_response:
            intent['responses'] = [new_response]

    with open(DATASET_PATH, 'w') as json_data:
        json.dump(updated_intents, json_data, indent=4)

    return redirect(url_for('admin'))

# Add route to handle adding new intents
@app.route('/add_intent', methods=['POST'])
@login_required
def add_intent():
    # Get the data for the new intent from the request
    new_tag = request.form.get('tag')
    new_patterns = request.form.get('patterns')
    new_responses = request.form.get('responses')
    new_context_set = request.form.get('context_set')
    
    # Load existing intents
    intents, _, _, _, _ = load_data_and_model()

    # Append new intent to the list
    new_intent = {
        "tag": new_tag,
        "patterns": [pattern.strip() for pattern in new_patterns.split('\n') if pattern.strip()],
        "responses": [response.strip() for response in new_responses.split('\n') if response.strip()],
        "context_set": new_context_set
    }
    intents['intents'].append(new_intent)

    # Save updated intents to dataset.json
    with open(DATASET_PATH, 'w') as json_data:
        json.dump(intents, json_data, indent=4)

    # Redirect back to the admin page
    return redirect(url_for('admin'))


# Route to render the page for adding a new intent
@app.route('/add_intent_page')
@login_required
def add_intent_page():
    return render_template('add_intent.html')


@app.route('/edit_responses')
@login_required
def edit_responses():
    intents, _, _, _, _ = load_data_and_model()
    return render_template('edit_responses.html', intents=intents['intents'])


@app.route('/train_model_page', methods=['GET'])
@login_required
def train_model_page():
        return render_template('train.html')
    

@app.route('/train_model', methods=['POST'])
@login_required
def train_model():
    # Ensure you set the correct path to your training script
    os.system('python NeuralNet\\Training\\train.py')
    return redirect(url_for('admin'))

# Add a route to provide training progress
@app.route('/get_training_progress', methods=['GET'])
def get_training_progress():
    try:
        with open('training_progress.txt', 'r') as file:
            progress = float(file.read())
        return jsonify({'progress': progress})
    except FileNotFoundError:
        abort(404)


# Define a dictionary of users (in a real application, you'd use a database)
users = {
    'admin': '123'
}

# Function to check if a username and password are valid
def is_valid_credentials(username, password):
    return users.get(username) == password

# Route to handle login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if is_valid_credentials(username, password):
            session['username'] = username
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

# Route to handle logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/delete_intent_page')
@login_required
def delete_intents_page():
    intents, _, _, _, _ = load_data_and_model()
    return render_template('delete_intent.html', intents=intents['intents'])

@app.route('/delete_intents', methods=['POST'])
@login_required
def delete_intents():
    intents_to_delete = request.form.getlist('intents_to_delete[]')
    if not intents_to_delete:
        abort(400, description="Intents to delete not provided")

    intents, _, _, _, _ = load_data_and_model()
    updated_intents = [intent for intent in intents['intents'] if intent['tag'] not in intents_to_delete]

    with open(DATASET_PATH, 'w') as json_data:
        json.dump({"intents": updated_intents}, json_data, indent=4)

    return redirect(url_for('admin'))



if __name__ == '__main__':
    app.run(debug=True)
