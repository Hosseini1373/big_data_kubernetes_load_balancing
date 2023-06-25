''''
This script is implementing a Flask web application for a Question-Answering (QA) system. Here's a high-level 
description of what it does:

Imports: The script imports all necessary libraries, such as Flask for web application, PyPDF2 for 
handling PDF files, and libraries for handling data and files.
Flask Initialization: It initializes a Flask application, sets up logging, and configures the static 
file directory.
Endpoints: The Flask app has several endpoints:
    A root endpoint (@app.route('/')) that serves an index.html file. This might be the home page of 
    your web application.
    A dynamic endpoint (@app.route('/<path:filename>')) that serves static files from a given directory. 
    This is typically used for serving CSS, JavaScript, or image files that are used by your HTML templates.
    A /query endpoint (@app.route('/query', methods=['GET'])) that takes a query parameter from a GET 
    request and passes it to a pipeline in the Haystack model. The model returns the top 3 results, 
    which are then printed to the standard output. The output is captured and returned as a JSON response.

Model Initialization: The script defines a function initializeModel() to initialize a Haystack model 
(imported from my_model.py). The model uses the FAISSDocumentStore for storage and retrieval of documents. 
If the model is already initialized, the function will return a message indicating so.
PDF to Text Conversion: The script includes a function under the endpoint /pdf for converting a PDF 
file into text. This function opens a PDF file, reads the text from each page, and writes the text to a 
file named tester.txt.
'''


# Importing necessary libraries
import json
import os
import pickle

import PyPDF2
import pandas as pd
from flask import Flask,request
import logging
from io import StringIO
import sys
from flask import Flask, jsonify
from os import path, walk
from haystack.document_stores import FAISSDocumentStore
from haystack.utils import print_documents
from my_model import MODELLFQA
from flask import send_from_directory, render_template

# Initialize Flask
extra_dirs = ['.']
extra_files = extra_dirs[:]
# Traverse through the directory tree and add all file paths to 'extra_files'
for extra_dir in extra_dirs:
    for dirname, dirs, files in walk(extra_dir):
        for filename in files:
            filename = path.join(dirname, filename)
            if path.isfile(filename):
                extra_files.append(filename)

app = Flask(__name__, static_folder='static')  # Define the Flask app
port = int(os.environ.get('PORT', 5000))  # Set the port number
# Set the logging configuration
logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
logging.getLogger("haystack").setLevel(logging.INFO)


@app.route('/<path:filename>')  # Define the route for serving static files
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)


@app.route('/')  # Define the route for the home page
def index():
    return render_template('index.html')


# Model Initialization
my_model = {}


def initializeModel():
    global my_model
    if './faiss_document_store.db' in extra_files and my_model:  # Check if the model is already initialized
        return "The model is already initialized"
    pdf_hash = {}
    my_model = MODELLFQA(pdf_hash)  # Initialize the model
    my_model.initializeModel()  # Call the model initialization method
    print("Initialized the model")
    return my_model


# Define the API for the query
@app.route('/query', methods=['GET'])
def query_result():
    initializeModel()  # Initialize the model
    query = request.args.get('query')  # Get the query from the request
    # Run the query through the model and get the top 3 results
    res = my_model.pipe.run(query=query, params={"Retriever": {"top_k": 3}})
    buffer = StringIO()  # Create a StringIO object
    sys.stdout = buffer  # Redirect stdout to the buffer
    print_documents(res, max_text_len=512)  # Print the results
    print_output = buffer.getvalue()  # Get the output from the buffer
    sys.stdout = sys.__stdout__  # Reset stdout
    res_json = {"queryResult": print_output}  # Create a response JSON
    response = jsonify(res_json)  # Create a Flask response
    response.headers.add('Access-Control-Allow-Origin', '*')  # Add the Access-Control-Allow-Origin header
    return response  # Return the response


 # Define the API for converting a PDF to text
@app.route('/pdf')
def pdf_to_txt(file):
    # Open the PDF File
    pdf_file = open(file, 'rb')  # Replace with your PDF file path

    # Create a PDF Reader Object
    pdf_reader = PyPDF2.PdfReader(pdf_file)

    # Get the total number of pages in the document
    total_pages = len(pdf_reader.pages)

    # Extract text from each page
    pdf_text = []

    for page in range(total_pages):
        text = pdf_reader.pages[page].extract_text()
        pdf_text.append(text)

    # Close the PDF File
    pdf_file.close()

    with open(r"tester.txt", "w", encoding='utf_8') as f2:
        f2.write(str(pdf_text))
    return 0

