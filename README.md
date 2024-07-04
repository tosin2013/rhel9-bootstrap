# RHEL 9 Bastion Configuration Workflow

This GitHub Actions workflow automates the configuration of a Red Hat Enterprise Linux 9 (RHEL 9) bastion host. Bastion hosts provide a secure and controlled entry point into a network.

## Workflow Triggers
* [configure-rhel9-bastion.yml](.github/workflows/configure-rhel9-bastion.yml)  
The workflow can be triggered in two ways:

* **Manual Trigger (workflow_dispatch):** 
   - Start the workflow from the "Actions" tab of your GitHub repository.
   - Provide input values for:
      - hostname
* **Webhook Trigger (repository_dispatch):**
   - Triggered by external systems using webhooks.
   - The webhook payload should include data for:
      - hostname

## Workflow Steps

1. **Set Environment Variables:**
   - Input parameters (hostname, domain, forwarder, etc.) are extracted and stored as environment variables for later use.

2. **Configure RHEL 9 Equinix Server:**
   - Establishes an SSH connection to the RHEL 9 server using provided credentials (stored in GitHub secrets).
   - Executes the following remote script actions:
      - Installs Git 
      - Clones or updates the `rhel9-bootstrap` repository.
      - Runs the `./setup-bastion.sh` script to perform core bastion configuration.

## setup-bastion.sh Script 

* **System Updates:**  Updates packages on the target system.
* **User Management:** Configures users and groups for access control.
* **Firewall Configuration:**  Adjusts firewall rules, limiting access to necessary ports.
* **SSH Hardening:** Modifies the SSH server's configuration for enhanced security.
* **Logging and Auditing:** Enables logging/auditing mechanisms.
* **OpenShift CLI (OC):** Installs the OC command-line tool for OpenShift interaction.
* **Ansible Setup:** Installs Ansible and Ansible Navigator for configuration management.
* **Ansible Vault Setup:** Configures Ansible Vault for secure data storage.


## Security

* This workflow utilizes GitHub secrets for storing sensitive credentials (username, SSH key, etc.). Ensure that you follow best practices for managing GitHub secrets.
