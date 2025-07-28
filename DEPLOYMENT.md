# Deploying to Google Cloud Run via Cloud Build

This document provides step-by-step instructions for deploying the Health Scoring Agent API to Google Cloud Run using an automated CI/CD pipeline with Cloud Build.

## Prerequisites

1.  **Google Cloud SDK:** Ensure you have the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed and configured on your local machine.
2.  **gcloud CLI:** Authenticate the `gcloud` CLI with your Google Cloud account:
    ```bash
    gcloud auth login
    gcloud auth application-default login
    ```
3.  **Google Cloud Project:** Have a Google Cloud project created with the following APIs enabled:
    *   Cloud Run API
    *   Artifact Registry API
    *   Cloud Build API
    You can enable them with the following commands, replacing `[PROJECT_ID]` with your project ID:
    ```bash
    gcloud services enable run.googleapis.com --project [PROJECT_ID]
    gcloud services enable artifactregistry.googleapis.com --project [PROJECT_ID]
    gcloud services enable cloudbuild.googleapis.com --project [PROJECT_ID]
    ```
4.  **Permissions:** Ensure the Cloud Build service account has the necessary IAM roles to deploy to Cloud Run and manage Artifact Registry.
    *   Go to the IAM page in the Google Cloud Console.
    *   Find the Cloud Build service account (`[PROJECT_NUMBER]@cloudbuild.gserviceaccount.com`).
    *   Grant it the "Cloud Run Admin" (`roles/run.admin`) and "Artifact Registry Writer" (`roles/artifactregistry.writer`) roles.

## Deployment Steps

### 1. Create an Artifact Registry Repository (One-Time Setup)

If you haven't already, create a Docker repository in Artifact Registry to store your container images.

```bash
export PROJECT_ID="your-gcp-project-id"
export REGION="your-gcp-region" # e.g., us-central1
export REPOSITORY="health-scoring-agent-repo"

gcloud artifacts repositories create $REPOSITORY \
    --repository-format=docker \
    --location=$REGION \
    --description="Docker repository for Health Scoring Agent"
```

### 2. Run the Cloud Build Pipeline

The `cloudbuild.yaml` file in this repository defines the entire build and deployment process. To trigger it, run the following command from the root of the repository:

```bash
gcloud builds submit --config cloudbuild.yaml .
```

This command will:
1.  Submit the code in the current directory to Cloud Build.
2.  Execute the steps defined in `cloudbuild.yaml`:
    *   Build the Docker image.
    *   Push the image to Artifact Registry.
    *   Deploy the new image to your Cloud Run service.

### Customizing the Deployment

You can override the default substitution variables in `cloudbuild.yaml` directly from the command line. For example, to deploy to a different region or with a different service name:

```bash
gcloud builds submit --config cloudbuild.yaml \
  --substitutions=_REGION="us-east1",_SERVICE_NAME="my-health-agent" .
```

After the build is complete, the command will output the URL of your deployed Cloud Run service.
