from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('eventdisbrow.html')

@app.route('/register')
def register():
    return render_template('eventregsys.html')

if __name__ == "__main__":
    app.run(debug=True)