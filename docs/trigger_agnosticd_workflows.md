# Trigger AgnosticD Workflows

This document explains how to trigger the GitHub workflow located at `.github/workflows/agnosticd-workflows.yml` using the `trigger_agnosticd_workflows.py` script.

## Prerequisites

- Python 3.x installed
- A GitHub personal access token with the necessary permissions to trigger workflows

## Running the Script

1. Open a terminal.
2. Navigate to the directory containing the `trigger_agnosticd_workflows.py` script.
3. Run the script using the following command:

   ```bash
   python3 trigger_agnosticd_workflows.py --owner YOUR_GITHUB_OWNER --repo YOUR_GITHUB_REPO --token YOUR_GITHUB_TOKEN --hostname YOUR_HOSTNAME --agnosticd_workload ocp4_workload_redhat_developer_hub --agnosticd_action create --guid YOUR_GUID --openshift_user YOUR_OPENSHIFT_USER 
   ```

4. Replace the placeholders with your actual values:
   - `YOUR_GITHUB_OWNER`: Your GitHub username or organization name.
   - `YOUR_GITHUB_REPO`: The name of your GitHub repository.
   - `YOUR_GITHUB_TOKEN`: Your GitHub personal access token.
   - `YOUR_HOSTNAME`: The hostname for the workflow.
   - `YOUR_GUID`: The GUID for the workflow.
   - `YOUR_OPENSHIFT_USER`: The OpenShift user for the workflow.

## Notes

- The script triggers the workflow on the `main` branch by default. If you need to trigger it on a different branch, add the `--branch` option with the desired branch name.

## Notes

- The script triggers the workflow on the `main` branch by default. If you need to trigger it on a different branch, modify the `ref` field in the script accordingly.
