from flask import Flask, render_template, request, jsonify
import json
import random
import torch
from NeuralNet.model import NeuralNet
from NeuralNet.utils import tokenize, stem, bag_of_words

app = Flask(__name__, static_url_path='/static')


def load_data_and_model():
    # Load intents data from a JSON file
    with open('NeuralNet\\dataset.json', 'r') as json_data:
        intents = json.load(json_data)

    # Load the pre-trained model and data
    FILE = "NeuralNet\\data.pth"
    data = torch.load(FILE)

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

    return intents, all_words, tags, model, device

def chatbot_response(intents, all_words, tags, model, device, sentence):
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
                return f"{random.choice(intent['responses'])}"
    else:
        return f"I do not understand your query , Please tell me in detail."

def run_chatbot(question):
    intents, all_words, tags, model, device = load_data_and_model()
    sentence = question
    response = chatbot_response(intents, all_words, tags, model, device, sentence)
    return response

# Route to render the index.html file
@app.route('/')

def index():
    return render_template('base.html')

# Route to handle POST requests for predicted response
@app.route('/get_response', methods=['POST'])
def get_response():
    # Get the question from the request
    question = request.json.get('question')
    
    # Process the question (you can replace this with your AI model logic)
    # For demonstration purposes, let's just return a simple response
    # predicted_response = f"You asked: '{question}'. This is the predicted response."
    predicted_response = run_chatbot(question)

    # Return the predicted response as JSON
    return ({'response': predicted_response})

if __name__ == '__main__':
    app.run(debug=True)
