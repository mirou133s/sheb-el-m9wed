from flask import flask 
from threading import thread 

app =flask('')
@app.route('/')
def home():
    return "Discord rahom mlih"

def run():
    app.run(host="0.0.0.0" , port=8080)

    def keep_alive(): 
        t = Thread(target=run)
        t.start()
