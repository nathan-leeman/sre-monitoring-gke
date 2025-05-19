# Starting the Kubernetes Application Locally on Minikube

This guide explains how to run the application locally using Minikube with either Hyper-V or Docker as the driver.

## Prerequisites

- [Minikube](https://minikube.sigs.k8s.io/docs/start/) installed.
- [Docker](https://www.docker.com/products/docker-desktop) installed.
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) installed.

## Option 1: Using Hyper-V

1. **Enable Hyper-V**:
   - Open PowerShell as Administrator and run:
     ```powershell
     Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
     ```
   - Restart your computer if prompted.

2. **Start Minikube with Hyper-V**:
   - Open PowerShell as Administrator and run:
     ```powershell
     minikube start --driver=hyperv
     ```

3. **Build the Docker Image**:
   - Navigate to your project directory and run:
     ```powershell
     docker build -t market-data-service:latest .
     ```

4. **Load the Image into Minikube**:
   - Run:
     ```powershell
     minikube image load market-data-service:latest
     ```

5. **Deploy the Application**:
   - Apply the Kubernetes manifests:
     ```powershell
     kubectl apply -f kubernetes/
     ```

6. **Check the Pods**:
   - Verify the pods are running:
     ```powershell
     kubectl get pods
     ```

7. **Access the Application**:
   - Open the service in your browser:
     ```powershell
     minikube service market-data-service
     ```

## Option 2: Using Docker (Fallback)

If Hyper-V doesn't work, you can use Docker as the driver:

1. **Start Minikube with Docker**:
   - Open PowerShell and run:
     ```powershell
     minikube start --driver=docker --memory=1900
     ```

2. **Build the Docker Image Inside Minikube**:
   - Point your shell to Minikube's Docker daemon:
     ```powershell
     & minikube docker-env --shell powershell | Invoke-Expression
     ```
   - Build the image:
     ```powershell
     docker build -t market-data-service:latest .
     ```

3. **Deploy the Application**:
   - Apply the Kubernetes manifests:
     ```powershell
     kubectl apply -f kubernetes/
     ```

4. **Check the Pods**:
   - Verify the pods are running:
     ```powershell
     kubectl get pods
     ```

5. **Access the Application**:
   - Open the service in your browser:
     ```powershell
     minikube service market-data-service
     ```

## Troubleshooting

- If you encounter permission issues with Hyper-V, ensure you're running PowerShell as Administrator.
- If the image fails to load, ensure you're using the correct Minikube profile and that the Docker daemon is running inside Minikube.

For more help, refer to the [Minikube documentation](https://minikube.sigs.k8s.io/docs/). 