import datetime
import pyjokes
import flask

app = flask.Flask(__name__)

@app.route("/time")
def time():

    return {
        "time": datetime.datetime.now().strftime("%H:%M")
    }

@app.route("/hour")
def hour():

    return {
        "hour": datetime.datetime.now().hour
    }

@app.route("/minute")
def hour():

    return {
        "hour": datetime.datetime.now().minute
    }

@app.route("/date")
def date():

    return {
        "date": datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    }

@app.route("/invoke_joke"):
def invoke_joke():

    return {
        "joke": pyjokes.get_joke()
    }

if __name__ == "__main__":
    app.run()