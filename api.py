from flask import Flask, jsonify
from flask_restful import Api

# Configuration
app = Flask(__name__)

# Endpoints
@app.route('/api', methods=['GET'])
def hello_world():
    return jsonify({'data': 'Hello, world!'})

if __name__ == "__main__":
    app.run(debug=True)
