# Deployment Instructions for Market Data Service

This document outlines the steps to deploy the Market Data Service to Google Kubernetes Engine (GKE).

## Prerequisites

1. Install required tools:
   ```bash
   # Install Google Cloud SDK
   # Visit: https://cloud.google.com/sdk/docs/install

   # Install kubectl
   gcloud components install kubectl

   # Install Docker
   # Visit: https://docs.docker.com/get-docker/
   ```

2. Configure Google Cloud:
   ```bash
   # Login to Google Cloud
   gcloud auth login

   # Set your project ID
   gcloud config set project [YOUR-PROJECT-ID]

   # Enable required APIs
   gcloud services enable container.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable monitoring.googleapis.com
   gcloud services enable logging.googleapis.com
   ```

## Deployment Steps

### 1. Create GKE Cluster

```bash
# Create a new cluster with monitoring enabled
gcloud container clusters create cluster-1 \
    --num-nodes=2 \
    --zone=us-east1-b \
    --machine-type=e2-medium \
    --enable-monitoring \
    --logging=SYSTEM,WORKLOAD

# Get credentials for kubectl
gcloud container clusters get-credentials cluster-1 --zone=us-east1-b
```

### 2. Create Namespace (Optional)

```bash
# Create a new namespace
kubectl create namespace [NAMESPACE-NAME]
```

### 3. Deploy Using Cloud Build

```bash
# Deploy to default namespace
gcloud builds submit

# OR deploy to specific namespace
gcloud builds submit --substitutions=_NAMESPACE=[NAMESPACE-NAME]
```

### 4. Verify Deployment

```bash
# Check deployment status
kubectl get deployments
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/market-data-service

# Check service endpoints
kubectl describe service market-data-service
```

## Monitoring

The application is configured with:
- Prometheus metrics at `/metrics`
- OpenTelemetry tracing
- Health check endpoint at `/health`

### Google Cloud Monitoring Setup

1. Enable Workload Identity (recommended for production):
   ```bash
   # Enable Workload Identity on the cluster
   gcloud container clusters update cluster-1 \
       --workload-pool=[YOUR-PROJECT-ID].svc.id.goog \
       --zone=us-east1-b
   ```

2. Create a service account for monitoring:
   ```bash
   # Create service account
   gcloud iam service-accounts create monitoring-sa \
       --display-name="Monitoring Service Account"

   # Grant monitoring permissions
   gcloud projects add-iam-policy-binding [YOUR-PROJECT-ID] \
       --member="serviceAccount:monitoring-sa@[YOUR-PROJECT-ID].iam.gserviceaccount.com" \
       --role="roles/monitoring.metricWriter"

   gcloud projects add-iam-policy-binding [YOUR-PROJECT-ID] \
       --member="serviceAccount:monitoring-sa@[YOUR-PROJECT-ID].iam.gserviceaccount.com" \
       --role="roles/logging.logWriter"
   ```

3. Update your deployment to use the service account:
   ```yaml
   # Add to your deployment.yaml
   spec:
     template:
       spec:
         serviceAccountName: monitoring-sa
   ```

4. View your metrics and logs:
   - Metrics: Visit https://console.cloud.google.com/monitoring
   - Logs: Visit https://console.cloud.google.com/logs

### Custom Metrics

To send custom metrics to Google Cloud Monitoring:

1. Add the following environment variables to your deployment:
   ```yaml
   env:
   - name: GOOGLE_CLOUD_PROJECT
     value: "[YOUR-PROJECT-ID]"
   - name: GOOGLE_APPLICATION_CREDENTIALS
     value: "/var/secrets/google/key.json"
   ```

2. Create a ConfigMap for your custom metrics:
   ```yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: custom-metrics-config
   data:
     metrics.yaml: |
       metrics:
         - name: custom_metric
           type: GAUGE
           description: "Custom metric description"
   ```

3. Apply the ConfigMap:
   ```bash
   kubectl apply -f custom-metrics-config.yaml
   ```

### Logging Best Practices

1. Use structured logging in your application:
   ```python
   import logging
   import json

   def log_structured(message, **kwargs):
       log_entry = {
           "message": message,
           **kwargs
       }
       logging.info(json.dumps(log_entry))
   ```

2. Add appropriate labels to your deployment:
   ```yaml
   metadata:
     labels:
       app: market-data-service
       environment: production
   ```

3. View logs in Cloud Logging:
   ```bash
   # View logs in real-time
   gcloud logging tail "resource.type=k8s_container AND resource.labels.cluster_name=cluster-1"
   ```

## Troubleshooting

1. If pods are not starting:
   ```bash
   kubectl describe pods
   kubectl logs [POD-NAME]
   ```

2. If service is not accessible:
   ```bash
   kubectl describe service market-data-service
   ```

3. To check Cloud Build logs:
   ```bash
   gcloud builds log [BUILD-ID]
   ```

## Cleanup

To remove the deployment:
```bash
# Delete the deployment and service
kubectl delete -f kubernetes/

# Delete the cluster
gcloud container clusters delete cluster-1 --zone=us-east1-b
```

## Additional Information

- The application runs on port 5000
- Metrics are exposed on the `/metrics` endpoint
- Health checks are performed on the `/health` endpoint
- OpenTelemetry collector endpoint is configured at `otel-collector:4317`

For more information, refer to:
- [GKE Documentation](https://cloud.google.com/kubernetes-engine/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/) 