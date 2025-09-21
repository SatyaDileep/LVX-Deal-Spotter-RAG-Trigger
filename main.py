import os
import logging
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
import functions_framework
import requests

FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID")
RAG_PROCESSOR_URL = os.environ.get("RAG_PROCESSOR_URL")

# Check for required environment variables
if not all([FIREBASE_PROJECT_ID, RAG_PROCESSOR_URL]):
    raise ValueError("Missing one or more required environment variables")

# Initialize Firebase Admin
if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        'databaseURL': f"https://{FIREBASE_PROJECT_ID}-default-rtdb.firebaseio.com"
    })

@functions_framework.cloud_event
def on_file_upload(cloud_event):
    try:
        data = cloud_event.data
        bucket = data['bucket']
        name = data['name']

        logging.info(f"Processing file: {name} from bucket: {bucket}")

        # Check for folder structure and extract deal_id
        if '/' not in name:
            logging.warning(f"File {name} is not in a deal folder. Skipping.")
            return

        deal_id = name.split('/')[0]

        # Supported file types
        supported_extensions = ['.pdf', '.docx', '.doc', '.txt', '.png', '.jpg', '.jpeg', '.ppt', '.pptx', '.mp4', '.mov', '.avi', '.mp3', '.wav', '.m4a']
        if not any(name.lower().endswith(ext) for ext in supported_extensions):
            logging.warning(f"File type for {name} not supported. Skipping.")
            return

        logging.info(f"Writing metadata to Realtime Database for file: {name}")
        # Write metadata to Realtime Database
        ref = db.reference('documents')
        new_ref = ref.push({
            'filename': name,
            'deal_id': deal_id,
            'upload_time': datetime.utcnow().isoformat()+'Z',
            'status': 'uploaded',
            'file_path': f"gs://{bucket}/{name}",
            'processed_content': '',
            'embeddings_stored': False
        })
        doc_id = new_ref.key
        logging.info(f"Successfully wrote metadata with doc_id: {doc_id}")

        logging.info(f"Triggering RAG processor for doc_id: {doc_id}")
        # Trigger RAG via HTTP
        url = RAG_PROCESSOR_URL + '/process'
        response = requests.post(url, json={'doc_id': doc_id, 'bucket': bucket, 'filename': name, 'deal_id': deal_id})
        response.raise_for_status() # Raise an exception for bad status codes
        logging.info(f"Successfully triggered RAG processor for doc_id: {doc_id}")

    except Exception as e:
        logging.error(f"An unexpected error occurred in on_file_upload: {str(e)}")