# OpenShift AI Workload Automation

## Overview

This document explains how to trigger the `openshift-ai-workload.sh` script in a GitHub Action or run it manually on a RHEL9 server. It also details the secrets needed to be loaded in GitHub Actions to run the pipeline properly.

## Running the Script Manually on a RHEL9 Server

### Prerequisites

1. Ensure that the RHEL9 server has the necessary dependencies installed:
   - `oc` (OpenShift command-line tool)
   - `yq` (YAML processor)
   - `openshift-install` (OpenShift installer)

2. Set the required environment variables:
   ```bash
   export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY_ID"
   export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_ACCESS_KEY"
   export AWS_REGION="YOUR_AWS_REGION"
   export BASE_DOMAIN="YOUR_BASE_DOMAIN"
   export CLUSTER_NAME="YOUR_CLUSTER_NAME"
   export PULL_SECRET_FILE="/path/to/your/pull-secret.json"
   ```

### Running the Script

1. Clone the repository to your RHEL9 server:
   ```bash
   git clone https://github.com/tosin2013/rhel9-bootstrap.git
   cd rhel9-bootstrap
   ```

2. Run the `openshift-ai-workload.sh` script with the required parameters:
   ```bash
   ./scripts/openshift-ai-workload.sh m6i.2xlarge us-east-2
   ```

   Optionally, you can add the `--destroy` flag to destroy the cluster:
   ```bash
   ./scripts/openshift-ai-workload.sh m6i.2xlarge us-east-2 --destroy
   ```

## Triggering the Script in a GitHub Action

### Prerequisites

1. Ensure that the GitHub repository has the necessary secrets configured:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`
   - `EMAIL`

### Workflow Configuration

The GitHub Actions workflow is configured in `.github/workflows/deploy-openshift-ai-workload.yaml`. The workflow is triggered on a push to the `main` branch or manually via the GitHub Actions UI. The workflow accepts the following inputs:
- `instance_size`: The instance size (e.g., `m6i.2xlarge`).
- `pull_secret_file`: The path to the pull secret file.
- `destroy`: Whether to destroy the cluster after deployment.
- `cluster_name`: The name of the cluster.
- `base_domain`: The base domain for the cluster.

### Secrets Configuration

To configure the secrets in your GitHub repository:

1. Go to your repository on GitHub.
2. Navigate to `Settings` > `Secrets and variables` > `Actions`.
3. Click on `New repository secret`.
4. Add the following secrets:
   - `AWS_ACCESS_KEY_ID`: Your AWS access key ID.
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key.
   - `AWS_REGION`: Your AWS region.

### Running the Workflow

1. Push changes to the `main` branch to trigger the workflow automatically.
2. Alternatively, you can manually trigger the workflow from the GitHub Actions UI:
   - Go to the `Actions` tab in your repository.
   - Select the `Deploy OpenShift AI Workload` workflow.
   - Click on `Run workflow` and provide the required inputs:
     - `instance_size`: The instance size (e.g., `m6i.2xlarge`).
     - `pull_secret_file`: The path to the pull secret file.
     - `destroy`: Whether to destroy the cluster after deployment.
     - `cluster_name`: The name of the cluster.
     - `base_domain`: The base domain for the cluster.

## Conclusion

This document provides a detailed guide on how to run the `openshift-ai-workload.sh` script manually on a RHEL9 server and how to trigger it in a GitHub Action. Ensure that the necessary secrets are configured in GitHub Actions to run the pipeline properly.
