# Trigger Pipeline Script Documentation

## Overview

The `trigger-pipeline.py` script is used to trigger a GitHub Actions workflow and update AWS secrets before triggering the workflow. This script is particularly useful for automating the deployment process of an OpenShift AI workload.

## Usage

To use the script, run it with the required command-line arguments. The script will update the AWS secrets and then trigger the specified GitHub Actions workflow.

### Command-Line Arguments

- `--repo-owner`: The GitHub repository owner (required).
- `--repo-name`: The GitHub repository name (required).
- `--workflow-id`: The GitHub workflow ID (default: `deploy-openshift-ai-workload.yaml`).
- `--instance-size`: The instance size (default: `m6i.2xlarge`).
- `--pull-secret-file`: The path to the pull secret file (default: `/home/lab-user/pull-secret.json`).
- `--destroy`: Whether to destroy the cluster after deployment (default: `false`).
- `--hostname`: The hostname (required).
- `--cluster-name`: The cluster name (default: `test-cluster`).
- `--base-domain`: The base domain (default: `example.com`).

### Example Command

```bash
python trigger-pipeline.py --repo-owner your-github-username --repo-name your-repo-name --hostname your-hostname
```

## Environment Variables

The script uses the following environment variables:

- `GITHUB_TOKEN`: The GitHub token for authentication.
- `NEW_AWS_ACCESS_KEY_ID`: The new AWS access key ID.
- `NEW_AWS_SECRET_ACCESS_KEY`: The new AWS secret access key.

## Functions

### update_secret(repo_owner, repo_name, token, secret_name, secret_value)

This function updates a GitHub Actions secret in the specified repository.

### trigger_workflow(repo_owner, repo_name, workflow_id, token, inputs)

This function triggers a GitHub Actions workflow with the specified inputs.

## Notes

- Ensure that the `GITHUB_TOKEN`, `NEW_AWS_ACCESS_KEY_ID`, and `NEW_AWS_SECRET_ACCESS_KEY` environment variables are set before running the script.
- The `key_id` in the `update_secret` function should be replaced with the actual key ID for encryption.
