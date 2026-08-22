#!/bin/bash
set -e

echo "======================================================================"
echo "         DEPLOYING AADHAAR ANALYTICS TO GCP CLOUD RUN"
echo "======================================================================"
echo "Project ID: vortex-arena-ai-92843"
echo "Region:     asia-south1"
echo "Service:    aadhaar-analytics-app"
echo "======================================================================"

gcloud config set project vortex-arena-ai-92843

gcloud run deploy aadhaar-analytics-app \
  --source . \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080

echo "======================================================================"
echo "Deployment finished successfully!"
echo "======================================================================"
