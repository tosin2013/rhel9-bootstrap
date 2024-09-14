#!/bin/bash
set -x
# Set a default repo name if not provided
#REPO_NAME=${REPO_NAME:-tosin2013/external-secrets-manager}

OC_VERSION=4.16 # 4.12 or 4.14
# https://github.com/mikefarah/yq/releases
YQ_VERSION=4.44.2


# Check for CICD PIPLINE FLAG
if [ -z "$CICD_PIPELINE" ]; then
    echo "CICD_PIPELINE is not set."
    echo "Running in interactive mode."
elif [ "$CICD_PIPELINE" == "true" ]; then
    echo "CICD_PIPELINE is set to $CICD_PIPELINE."
    echo "Running in non-interactive mode."
    # Check if the AWS variables are defined and not empty
    if [ -z "${SSH_PASSWORD}" ]; then
      echo "SSH_PASSWORD variable not found or empty. Exiting..."
      exit 1
    fi
else
    echo "CICD_PIPELINE is not set."
    echo "Running in interactive mode."
fi


if [ -z $GUID ]; then 
     read -p "Enter GUID: " GUID
fi


if [[ -s ~/.vault_password ]]; then
    echo "The file contains information."
else
    curl -OL https://gist.githubusercontent.com/tosin2013/022841d90216df8617244ab6d6aceaf8/raw/92400b9e459351d204feb67b985c08df6477d7fa/ansible_vault_setup.sh
    chmod +x ansible_vault_setup.sh
    echo "Configuring password for Ansible Vault"
    if [ $CICD_PIPELINE == "true" ];
    then
        if [ -z "$SSH_PASSWORD" ]; then
            echo "SSH_PASSWORD enviornment variable is not set"
            exit 1
        fi
        echo "$SSH_PASSWORD" > ~/.vault_password
        sudo cp ~/.vault_password /root/.vault_password
        sudo cp ~/.vault_password /home/lab-user/.vault_password
        bash  ./ansible_vault_setup.sh
    else
        bash  ./ansible_vault_setup.sh
    fi
fi

# Ensure Git is installed
echo "Installing Git..."
sudo dnf install -yq git
if ! yq -v  &> /dev/null
then
    VERSION=v${YQ_VERSION}
    BINARY=yq_linux_amd64
    sudo wget https://github.com/mikefarah/yq/releases/download/${VERSION}/${BINARY} -O /usr/bin/yq &&\
    sudo chmod +x /usr/bin/yq
fi

if ! helm -v  &> /dev/null
then
    echo "helm not found. Installing..."
    curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
    chmod 700 get_helm.sh
    ./get_helm.sh
fi

# Install System Packages
if [ ! -f /usr/bin/podman ]; then
  ./scripts/partial-rpm-packages.sh
fi

# Run the configuration script to setup the bastion host with:
# - Python 3.9
# - Ansible
# - Ansible Navigator
# - Pip modules
if ! command -v ansible-navigator &> /dev/null; then
    echo "ansible-navigator not found. Installing..."
    if ! sudo subscription-manager repos --enable=ansible-automation-platform-2.4-for-rhel-9-x86_64-rpms &> /dev/null; then
        echo "subscription-manager command not found. Installing ansible-navigator using pip..."
        sudo dnf install -y python3-pip
        python3 -m pip install ansible-navigator --user
        echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.profile
        source ~/.profile
    else
        sudo subscription-manager repos --enable=ansible-automation-platform-2.4-for-rhel-9-x86_64-rpms || exit $?
        sudo dnf -y install ansible-navigator
        ansible-navigator --version
    fi
else
    echo "ansible-navigator is already installed. Skipping installation."
fi


# Install OCP CLI Tools
if [ ! -f /usr/bin/oc ]; then
  ./scripts/partial-setup-ocp-cli.sh
fi
