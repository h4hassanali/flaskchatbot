from flask import Flask, render_template, request, jsonify

app = Flask(__name__, static_url_path='/static')

# Route to render the index.html file


def index():
    return render_template('index.html')

# Route to handle POST requests for predicted response
@app.route('/get_response', methods=['POST'])
def get_response():
    # Get the question from the request
    question = request.json.get('question')
    question = question + "Hsdnajkdhh"
    # Process the question (you can replace this with your AI model logic)
    # For demonstration purposes, let's just return a simple response
    predicted_response = f"You asked: '{question}'. This is the predicted response."
    
    # Return the predicted response as JSON
    return ({'response': predicted_response})

if __name__ == '__main__':
    app.run(debug=True)
