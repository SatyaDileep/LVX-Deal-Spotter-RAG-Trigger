# LVX-Deal-Spotter-RAG-Trigger

This repository contains a Google Cloud Function that triggers the RAG (Retrieval-Augmented Generation) processing pipeline for the LVX Deal Spotter application. The function is triggered by file uploads to a Google Cloud Storage bucket.

## Functionality

- **Triggered by Cloud Storage:** The function is configured to be triggered whenever a new file is uploaded to a specified Google Cloud Storage bucket.
- **Metadata Logging:** Upon trigger, it logs metadata about the uploaded file (filename, deal ID, upload time, etc.) to a Firebase Realtime Database.
- **Invokes RAG Processor:** It then makes an HTTP POST request to the `rag-processor` service to initiate the actual document processing.
- **File Type Filtering:** The function checks for supported file extensions and will only trigger the processor for supported file types.

## Environment Variables

The following environment variables are required for the function to run:

- `FIREBASE_PROJECT_ID`: Your Firebase project ID.
- `RAG_PROCESSOR_URL`: The URL of the deployed `rag-processor` service.

## Trigger

- **Event Type:** `google.cloud.storage.object.v1.finalized`
- **Bucket:** The name of your Google Cloud Storage bucket where files are uploaded.

## Dependencies

- `firebase-admin`: To connect to the Firebase Realtime Database.
- `functions-framework`: The framework for writing Google Cloud Functions.
- `requests`: To make HTTP requests to the `rag-processor` service.

For a full list of dependencies, see `requirements.txt`.

## Deployment

To deploy this function, you can use the `gcloud` command-line tool:

```bash
gcloud functions deploy on_file_upload \
  --runtime python312 \
  --trigger-resource YOUR_GCS_BUCKET_NAME \
  --trigger-event google.storage.object.finalize \
  --entry-point on_file_upload \
  --env-vars-file .env.yaml
```

Make sure you have a `.env.yaml` file with the required environment variables:

```yaml
FIREBASE_PROJECT_ID: your-firebase-project-id
RAG_PROCESSOR_URL: your-rag-processor-url
```
