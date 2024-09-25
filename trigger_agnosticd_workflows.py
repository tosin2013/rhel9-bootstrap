import requests

def trigger_workflow(owner, repo, token, branch="main", inputs=None):
    """
    Trigger the GitHub workflow located at .github/workflows/agnosticd-workflows.yml
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/agnosticd-workflows.yml/dispatches"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "ref": branch,
        "inputs": inputs or {}
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 204:
        print("Workflow triggered successfully.")
    else:
        print(f"Failed to trigger workflow. Status code: {response.status_code}")
        print(response.json())

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Trigger AgnosticD workflows")
    parser.add_argument("--owner", required=True, help="GitHub repository owner")
    parser.add_argument("--repo", required=True, help="GitHub repository name")
    parser.add_argument("--token", required=True, help="GitHub personal access token")
    parser.add_argument("--branch", default="main", help="Branch to trigger the workflow on")
    parser.add_argument("--hostname", help="Hostname for the workflow")
    parser.add_argument("--agnosticd_repo", default="https://github.com/tosin2013/agnosticd.git", help="AgnosticD repository URL")
    parser.add_argument("--agnosticd_workload", required=True, choices=["ocp4_workload_redhat_developer_hub"], help="AgnosticD workload to deploy")
    parser.add_argument("--agnosticd_action", required=True, choices=["create", "remove"], help="AgnosticD action to perform")
    parser.add_argument("--guid", required=True, help="GUID")
    parser.add_argument("--openshift_user", required=True, help="OpenShift user")
    
    args = parser.parse_args()
    
    inputs = {
        "hostname": args.hostname,
        "agnosticd_repo": args.agnosticd_repo,
        "agnosticd_workload": args.agnosticd_workload,
        "agnosticd_action": args.agnosticd_action,
        "guid": args.guid,
        "openshift_user": args.openshift_user
    }
    
    trigger_workflow(args.owner, args.repo, args.token, args.branch, inputs)
