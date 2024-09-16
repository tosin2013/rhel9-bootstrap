import requests
import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import base64

def get_public_key(repo_owner, repo_name, token):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/secrets/public-key"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch public key: {response.status_code} - {response.text}")

def encrypt_secret(public_key_info, secret_value):
    public_key = serialization.load_pem_public_key(public_key_info['key'].encode())
    encrypted_value = public_key.encrypt(
        secret_value.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return base64.b64encode(encrypted_value).decode()

def update_secret(repo_owner, repo_name, token, secret_name, secret_value):
    public_key_info = get_public_key(repo_owner, repo_name, token)
    encrypted_value = encrypt_secret(public_key_info, secret_value)
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/secrets/{secret_name}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {
        "encrypted_value": encrypted_value,
        "key_id": public_key_info['key_id']
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

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trigger GitHub workflow and update AWS secrets.")
    parser.add_argument("--repo-owner", required=True, help="GitHub repository owner")
    parser.add_argument("--repo-name", required=True, help="GitHub repository name")
    parser.add_argument("--workflow-id", default="deploy-openshift-ai-workload.yaml", help="GitHub workflow ID")
    parser.add_argument("--instance-size", default="m6i.2xlarge", help="Instance size")
    parser.add_argument("--pull-secret-file", default="/home/lab-user/pull-secret.json", help="Path to the pull secret file")
    parser.add_argument("--destroy", default="false", help="Destroy the cluster after deployment")
    parser.add_argument("--hostname", required=True, help="Hostname")
    parser.add_argument("--cluster-name", default="test-cluster", help="Cluster name")
    parser.add_argument("--base-domain", default="example.com", help="Base domain")

    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN")
    inputs = {
        "instance_size": args.instance_size,
        "pull_secret_file": args.pull_secret_file,
        "destroy": args.destroy,
        "hostname": args.hostname,
        "cluster_name": args.cluster_name,
        "base_domain": args.base_domain
    }

    # Update AWS secrets
    update_secret(args.repo_owner, args.repo_name, token, "AWS_ACCESS_KEY_ID", os.getenv("NEW_AWS_ACCESS_KEY_ID"))
    update_secret(args.repo_owner, args.repo_name, token, "AWS_SECRET_ACCESS_KEY", os.getenv("NEW_AWS_SECRET_ACCESS_KEY"))

    # Trigger the workflow
    trigger_workflow(args.repo_owner, args.repo_name, args.workflow_id, token, inputs)
