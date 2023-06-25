
''''
 this script defines a Flask-based application that is focused on initializing 
 and using a question-answering model based on the Hugging Face's Transformers. 
 The goal is to provide an interface to retrieve and generate answers to questions based on a pre-defined knowledge base.

Here's a summary of its functionality:

It defines a class MODELLFQA that encapsulates the operations related to the model.
The initializeModel method is responsible for setting up the model and associated components, 
including the document store, the retriever, and the generator.
If the index of embeddings ("indexes") does not exist, the method fetches a predefined archive of documents
from an external URL, processes these documents, and stores them into a FAISSDocumentStore.
The DensePassageRetriever is initialized with specified models for question and context embeddings. It is 
then used to update the embeddings in the document store.
The Seq2SeqGenerator is initialized with a specified model and used along with the retriever to create a 
GenerativeQAPipeline. This pipeline is designed to answer questions based on the documents in the store.
It also includes some unused functionality (commented out) related to testing the retriever, saving the 
pipeline, and checking whether a certain hash already exists.

Please note that the actual Flask application and its routes are not defined in this script. The script is
mainly focused on defining and initializing the question-answering model that will be used by the application.
'''


# Importing necessary libraries
import os
import pickle
from flask import Flask
import logging
from io import StringIO
import sys
from flask import Flask, render_template,jsonify
from os import path, walk
import json
import pandas as pd
from haystack.document_stores import FAISSDocumentStore
from haystack.utils import convert_files_to_docs, fetch_archive_from_http, clean_wiki_text
from haystack.nodes import DensePassageRetriever
from haystack.utils import print_documents
from haystack.pipelines import DocumentSearchPipeline
from haystack.nodes import Seq2SeqGenerator
from haystack.pipelines import GenerativeQAPipeline

# Class for model LFQA
class MODELLFQA:
    # Initialization
    def __init__(self, hash):
        self.pipe = {} # Initializes pipeline dictionary
        self.hash = hash # Initializes hash value

    # Model initialization
    def initializeModel(self):
        # Check if the index file already exists
        if not os.path.isfile("indexes"):
            # If it doesn't exist, create a new FAISS document store
            document_store = FAISSDocumentStore(embedding_dim=128, faiss_index_factory_str="Flat")
            # Define the location of the documents and the source of the documents
            doc_dir = "data/tutorial12"
            s3_url = "https://s3.eu-central-1.amazonaws.com/deepset.ai-farm-qa/datasets/documents/wiki_gameofthrones_txt12.zip"
            # Fetch the documents from the source
            fetch_archive_from_http(url=s3_url, output_dir=doc_dir)
            # Convert the documents into a suitable format
            docs = convert_files_to_docs(dir_path=doc_dir, clean_func=clean_wiki_text, split_paragraphs=True)
            # Write the documents into the document store
            document_store.write_documents(docs)
            # Initialize the retriever with the document store and the specific models for query and passage encoding
            retriever = DensePassageRetriever(
                document_store=document_store,
                query_embedding_model="vblagoje/dpr-question_encoder-single-lfqa-wiki",
                passage_embedding_model="vblagoje/dpr-ctx_encoder-single-lfqa-wiki",
            )
            # Update the document store with the embeddings from the retriever
            document_store.update_embeddings(retriever)
            # Save the document store
            document_store.save(index_path = 'indexes')
        else:
            # If the index file already exists, load the document store from the index file
            print("reading from saved model:")
            document_store = FAISSDocumentStore(faiss_index_path="indexes", faiss_config_path="indexes.json")
            document_store = FAISSDocumentStore.load(index_path="indexes")
            # Initialize the retriever with the document store and the specific models for query and passage encoding
            retriever = DensePassageRetriever(
                document_store=document_store,
                query_embedding_model="vblagoje/dpr-question_encoder-single-lfqa-wiki",
                passage_embedding_model="vblagoje/dpr-ctx_encoder-single-lfqa-wiki",
            )        
        # Initialize the generator model
        generator = Seq2SeqGenerator(model_name_or_path="vblagoje/bart_lfqa")
        # Create the pipeline with the generator and the retriever
        self.pipe = GenerativeQAPipeline(generator, retriever)

    # Function to check if a hash already exists
    def existhash(hashes):
        # Check if the hash file already exists
        if os.path.isfile('embedding_hashes.csv'):
            # Open the file containing available embeddings
            with open('embeddings_available.json', 'w') as f:
                x = json.load(f)
            # Check if the hash is in the list of available embeddings
            if hashes in x['hash']:
                return True  # Hash is in list, no need to redo
            # If the hash is not in the list, add it
            x['hash'].append(hashes)
            # Write the updated list back to the file
            json.dump(x, f)
        else:
            # If the file doesn't exist, create a new file and add the hash to it
            x = {}
            with open('embeddings_available.json', 'w') as f:
                x['hash'] = [hashes]
                json.dump(x, f)
        # Return false if the file didn't exist or the hash wasn't in the list
        return False