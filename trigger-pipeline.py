import requests
import os
import base64
import nacl.encoding
import nacl.public
import argparse

def get_public_key(repo_owner, repo_name, token):
    """
    Fetches the public key for a GitHub repository's secrets.

    Args:
        repo_owner (str): Owner of the repository.
        repo_name (str): Name of the repository.
        token (str): GitHub access token.

    Returns:
        dict: JSON response containing 'key' and 'key_id'.
    """
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
    """
    Encrypts a secret using the repository's public key.

    Args:
        public_key_info (dict): Dictionary containing 'key' and 'key_id'.
        secret_value (str): The secret value to encrypt.

    Returns:
        str: Base64-encoded encrypted secret.
    """
    # Decode the Base64-encoded public key
    public_key = nacl.public.PublicKey(public_key_info['key'], nacl.encoding.Base64Encoder)
    
    # Create a SealedBox with the public key
    sealed_box = nacl.public.SealedBox(public_key)
    
    # Encrypt the secret
    encrypted = sealed_box.encrypt(secret_value.encode())
    
    # Return the Base64-encoded encrypted secret
    return base64.b64encode(encrypted).decode()

def update_secret(repo_owner, repo_name, token, secret_name, secret_value):
    """
    Updates or creates a secret in the GitHub repository.

    Args:
        repo_owner (str): Owner of the repository.
        repo_name (str): Name of the repository.
        token (str): GitHub access token.
        secret_name (str): Name of the secret to update.
        secret_value (str): Value of the secret to encrypt and store.
    """
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
        print(f"Secret '{secret_name}' updated successfully.")
    else:
        raise Exception(f"Failed to update secret '{secret_name}': {response.status_code} - {response.text}")

def trigger_workflow(repo_owner, repo_name, workflow_id, token, inputs):
    """
    Triggers a GitHub Actions workflow.

    Args:
        repo_owner (str): Owner of the repository.
        repo_name (str): Name of the repository.
        workflow_id (str): ID or filename of the workflow to trigger.
        token (str): GitHub access token.
        inputs (dict): Inputs to pass to the workflow.
    """
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
        raise Exception(f"Failed to trigger workflow: {response.status_code} - {response.text}")

def main():
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
    if not token:
        raise EnvironmentError("GITHUB_TOKEN environment variable is not set.")

    inputs = {
        "instance_size": args.instance_size,
        "pull_secret_file": args.pull_secret_file,
        "destroy": args.destroy,
        "hostname": args.hostname,
        "cluster_name": args.cluster_name,
        "base_domain": args.base_domain
    }

    # Update AWS secrets
    aws_access_key_id = os.getenv("NEW_AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("NEW_AWS_SECRET_ACCESS_KEY")

    if not aws_access_key_id or not aws_secret_access_key:
        raise EnvironmentError("AWS credentials are not set in environment variables.")

    update_secret(args.repo_owner, args.repo_name, token, "AWS_ACCESS_KEY_ID", aws_access_key_id)
    update_secret(args.repo_owner, args.repo_name, token, "AWS_SECRET_ACCESS_KEY", aws_secret_access_key)

    # Trigger the workflow
    trigger_workflow(args.repo_owner, args.repo_name, args.workflow_id, token, inputs)

if __name__ == "__main__":
    main()
