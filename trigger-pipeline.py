import requests
import os

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
    trigger_workflow(repo_owner, repo_name, workflow_id, token, inputs)
