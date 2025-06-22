from flask import Flask, render_template, request
from utils import predict_score

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        result = predict_score(request.form)
        return render_template('results.html', result=result)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
