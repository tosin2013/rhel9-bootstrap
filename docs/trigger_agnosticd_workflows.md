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
   python3 trigger_agnosticd_workflows.py
   ```

4. Ensure you have replaced `YOUR_GITHUB_TOKEN` in the script with your actual GitHub token.

## Notes

- The script triggers the workflow on the `main` branch by default. If you need to trigger it on a different branch, modify the `ref` field in the script accordingly.
