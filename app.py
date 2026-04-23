from flask import Flask, flash, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('EventDis&Brow.html')

if __name__ == "__main__":
    app.run(debug=True)