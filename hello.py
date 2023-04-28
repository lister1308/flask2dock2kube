from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return '<h1>Hello NEW World from Flask!</h1>'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int("12345"), debug=True)
