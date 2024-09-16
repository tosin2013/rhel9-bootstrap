import requests
import os

def update_secret(repo_owner, repo_name, token, secret_name, secret_value):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/secrets/{secret_name}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {
        "encrypted_value": secret_value,
        "key_id": "your-key-id"  # This should be replaced with the actual key ID
    }
    response = requests.put(url, json=data, headers=headers)
    if response.status_code == 204:
        print(f"Secret {secret_name} updated successfully.")
    else:
        print(f"Failed to update secret {secret_name}: {response.status_code} - {response.text}")

def trigger_workflow(repo_owner, repo_name, workflow_id, token, inputs):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/{workflow_id}/dispatches"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {
        "ref": "main",  # or the branch you want to trigger the workflow on
        "inputs": inputs
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 204:
        print("Workflow triggered successfully.")
    else:
        print(f"Failed to trigger workflow: {response.status_code} - {response.text}")

if __name__ == "__main__":
    repo_owner = "your-github-username"
    repo_name = "your-repo-name"
    workflow_id = "deploy-openshift-ai-workload.yaml"
    token = os.getenv("GITHUB_TOKEN")
    inputs = {
        "instance_size": "m6i.2xlarge",
        "pull_secret_file": "/home/lab-user/pull-secret.json",
        "destroy": "false",
        "hostname": "your-hostname",
        "cluster_name": "test-cluster",
        "base_domain": "example.com"
    }

    # Update AWS secrets
    update_secret(repo_owner, repo_name, token, "AWS_ACCESS_KEY_ID", os.getenv("NEW_AWS_ACCESS_KEY_ID"))
    update_secret(repo_owner, repo_name, token, "AWS_SECRET_ACCESS_KEY", os.getenv("NEW_AWS_SECRET_ACCESS_KEY"))

    # Trigger the workflow
    trigger_workflow(repo_owner, repo_name, workflow_id, token, inputs)
