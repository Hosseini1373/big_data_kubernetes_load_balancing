# BigDataProjekt

# API Load Testing and Deployment

This project aims to perform load testing on a local API server and deploy the application to a Kubernetes cluster. It includes scripts, configurations, and instructions for load testing the API server, deploying the application to a local Minikube cluster, and deploying it to a production Kubernetes cluster.

## Load Testing

The analyis scripts are used to perform load testing on a local and remote K8 API server. It sends multiple simultaneous requests to the server and measures its performance under stress. The script logs the number of successful responses, timeouts, average response time, and total time taken for each set of concurrent requests. The results are stored in CSV files and visualized using various types of plots.

## Load Testing

The data folder contains all the documents that are related to game of thrones.

### Prerequisites

To run the load test, make sure you have the following dependencies installed:

- Python (version 3.x)
- `requests` library
- `matplotlib` library
- `numpy` library
- `pandas` library

### Running the Load Test

1. Clone this repository to your local machine.
2. Navigate to the project directory: `cd api-load-test-and-deployment`.
3. Run the load test script: `python ApiAnalysis.py`, `python ApiAnalysisLocal.py`,`python ApiAnalysisSequential.py` or `python ApiAnalysisSequentialLocal.py` The resulting figures and CSVs will be saved in the folder images.

## Deployment to Kubernetes

The project includes scripts and configuration files for deploying the application to a Kubernetes cluster.

### Local Minikube Deployment

For local testing, you can use the `Minikube_local_app_deploy.yaml` file to deploy the application to a Minikube cluster. This allows you to test the application's functionality and performance in a local Kubernetes environment.

#### Prerequisites

- Minikube installed and running
- Docker installed

#### Deploying to Minikube

1. Build the Docker image for the application: `docker build -t your-image-name .`
2. Start Minikube: `minikube start`
3. Set the Docker environment to use Minikube's Docker daemon: `eval $(minikube docker-env)`
4. Deploy the application: `kubectl apply -f Minikube_local_app_deploy.yaml`
5. Verify that the deployment and associated services are running correctly using `kubectl`.

### Production Deployment

To deploy the application to a production Kubernetes cluster, follow these steps:

#### Prerequisites

- Access to a running Kubernetes cluster
- Docker image of the application pushed to a container registry accessible by the cluster

#### Deploying to Production

1. Update the `K8_app_deployment.yaml` file with the appropriate image details and configuration for your environment.
2. Deploy the application: `kubectl apply -f K8_app_deployment.yaml`
3. Apply the Ingress configuration: `kubectl apply -f K8_ingress_deploy.yaml`
4. Verify that the deployment, services, and ingress are set up correctly using `kubectl`.

## Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)

## License

This project is licensed under the [MIT License](LICENSE).
