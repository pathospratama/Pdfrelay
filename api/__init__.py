from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)

@app.route('/')
def home():
    return "PDF Processor API"

# Import all endpoints
from . import process_pdf, health