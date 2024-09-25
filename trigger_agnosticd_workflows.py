import requests

def trigger_workflow():
    """
    Trigger the GitHub workflow located at .github/workflows/agnosticd-workflows.yml
    """
    url = "https://api.github.com/repos/{owner}/{repo}/actions/workflows/agnosticd-workflows.yml/dispatches"
    headers = {
        "Authorization": "token YOUR_GITHUB_TOKEN",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "ref": "main"  # or the branch you want to trigger the workflow on
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 204:
        print("Workflow triggered successfully.")
    else:
        print(f"Failed to trigger workflow. Status code: {response.status_code}")
        print(response.json())

if __name__ == "__main__":
    trigger_workflow()
