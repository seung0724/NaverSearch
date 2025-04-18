from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/analyzeData', methods=['POST'])
def analyze_data():
    data = request.get_json()
    print("📥 받은 데이터:", data)
    
    result = {
        "status": "ok",
        "length": len(data.get("text", ""))
    }
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)
