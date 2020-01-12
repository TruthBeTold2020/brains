from flask import Flask, redirect, render_template, request

from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from google.protobuf.json_format import MessageToDict,MessageToJson
from flask_cors import CORS

import json

app = Flask(__name__)
CORS(app)


@app.route('/')
def homepage():
    # Return a Jinja2 HTML template of the homepage.
    return render_template('homepage.html')

@app.route('/run_language', methods=['GET', 'POST'])
def run_language():
    # Create a Cloud Natural Language client
    client = language.LanguageServiceClient()

    # Retrieve inputted text from the form and create document object
    text = request.form['text']
    document = types.Document(content=text, type=enums.Document.Type.PLAIN_TEXT)

    # Retrieve response from Natural Language API's analyze_entities() method
    response = client.analyze_entities(document)
    entities = response.entities

    # Retrieve response from Natural Language API's analyze_sentiment() method
    response = client.analyze_sentiment(document)
    sentiment = response.document_sentiment

    # Retrieve category and confidence level
    response = client.classify_text(document)
    categories = response.categories

    result = {}
    for category in categories:
        # Turn the categories into a dictionary of the form:
        # {category.name: category.confidence}, so that they can
        # be treated as a sparse vector.
        result[category.name] = category.confidence
    print(text)
    for category in categories:
        text = text + 'category: ' + category.name
        text = text + 'confidence: ' + str(category.confidence)

    # Return a Jinja2 HTML template of the homepage and pass the 'text', 'entities',
    # and 'sentiment' variables to the frontend. These contain information retrieved
    # from the Natural Language API.
    return render_template('homepage.html', text=text, entities=entities, sentiment=sentiment)

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    # Create a Cloud Natural Language client
    client = language.LanguageServiceClient()

    # Retrieve inputted text from the form and create document object
    text = request.form['text']
    document = types.Document(content=text, type=enums.Document.Type.PLAIN_TEXT)

    # Retrieve response from Natural Language API's analyze_entities() method
    response_entities = client.analyze_entities(document)

    # Retrieve response from Natural Language API's analyze_sentiment() method
    response_sentiment = client.analyze_sentiment(document)

    # Retrieve category and confidence level
    response_categories = client.classify_text(document)

    return json.dumps({'entities': MessageToDict(response_entities), 'sentiment': MessageToDict(response_sentiment),
                       'category': MessageToDict(response_categories)})

@app.errorhandler(500)
def server_error(e):
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
