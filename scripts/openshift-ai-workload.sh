#!/bin/bash

# Check if instance size and region are provided
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Instance size or region not provided. Please pass the instance size and AWS region as arguments."
  echo "Example: ./openshift-ai-workload.sh m6i.2xlarge us-east-2"
  exit 1
fi

instance_size=$1
region=$2

print_aws_variables() {
    echo "Export the following AWS variables before running this script:"
    echo "export aws_access_key_id=\"YOUR_ACCESS_KEY_ID\""
    echo "export aws_secret_access_key=\"YOUR_SECRET_ACCESS_KEY\""
    echo "export aws_region=\"YOUR_AWS_REGION\""
}

# Check if AWS credentials are set
if [ -z ${aws_access_key_id} ]; then
    echo "aws_access_key_id is not set"
    print_aws_variables
    exit 1
fi

if [ -z ${aws_secret_access_key} ]; then
    echo "aws_secret_access_key is not set"
    print_aws_variables
    exit 1
fi

if [ -z ${aws_region} ]; then
    echo "aws_region is not set"
    print_aws_variables
    exit 1
fi

# Check if 'yq' is installed
if ! yq -v &> /dev/null; then
    VERSION=v4.34.1
    BINARY=yq_linux_amd64
    sudo wget https://github.com/mikefarah/yq/releases/download/${VERSION}/${BINARY} -O /usr/bin/yq &&\
    sudo chmod +x /usr/bin/yq
fi

# Check if 'oc' is installed
if ! command -v oc &> /dev/null; then
  echo "'oc' (OpenShift command-line tool) is not installed. Installing and configuring..."
  
  # Download the 'configure-openshift-packages.sh' script
  curl -OL https://raw.githubusercontent.com/tosin2013/openshift-4-deployment-notes/master/pre-steps/configure-openshift-packages.sh

  # Make the script executable
  chmod +x configure-openshift-packages.sh 

  # Run the 'configure-openshift-packages.sh' script with the -i flag for installation
  ./configure-openshift-packages.sh -i
else
  echo "'oc' (OpenShift command-line tool) is already installed. Skipping installation."
fi

# Check if SSH key exists and generate if not
ssh_key_file="/home/$USER/.ssh/cluster-key"
if [ ! -f "$ssh_key_file" ]; then
  echo "SSH key '/home/$USER/.ssh/cluster-key' does not exist. Generating..."
  ssh-keygen -t rsa -b 4096 -f /home/$USER/.ssh/cluster-key -N ''
else
  echo "SSH key '/home/$USER/.ssh/cluster-key' already exists. Skipping key generation."
fi

# Create install-config.yaml for m6i.2xlarge workers
openshift-install create install-config --dir=cluster

# Update worker nodes to m6i.2xlarge without zone or metadataService configurations
echo "Updating worker nodes to m6i.2xlarge..."
yq -i eval '.compute[0].hyperthreading = "Enabled" |
     .compute[0].name = "worker" |
     .compute[0].platform.aws.rootVolume.iops = 2000 |
     .compute[0].platform.aws.rootVolume.size = 500 |
     .compute[0].platform.aws.rootVolume.type = "io1" |
     .compute[0].platform.aws.type = "m6i.2xlarge" |
     .compute[0].replicas = 3' cluster/install-config.yaml

# Create the cluster with standard workers
openshift-install create cluster --dir=$HOME/cluster --log-level debug

# Sleep to ensure the cluster is stable
echo "Waiting for the cluster to stabilize..."
sleep 300  # Wait for 5 minutes

# Login to OpenShift
echo "Logging in to OpenShift..."
export KUBECONFIG=/home/$USER/cluster/auth/kubeconfig
oc whoami

# Copy an existing MachineSet
echo "Copying an existing MachineSet..."
oc get machineset -n openshift-machine-api -o json | jq '.items[0]' > original-machineset.json

# Modify the copied MachineSet for GPU nodes (p2.xlarge)
echo "Modifying the copied MachineSet for GPU nodes..."
jq '.metadata.name = "gpu-workers" |
    .spec.replicas = 2 |
    .spec.template.spec.providerSpec.value.instanceType = "p2.xlarge"' original-machineset.json > gpu-machineset.json

# Apply the new GPU MachineSet
echo "Applying the new GPU MachineSet..."
oc apply -f gpu-machineset.json

# Flag for destroying the cluster and deleting the $HOME/cluster folder
if [ "$3" == "--destroy" ]; then
  echo "Destroying the cluster and deleting the $HOME/cluster folder..."
  openshift-install destroy cluster --dir=$HOME/cluster --log-level debug
  rm -rf $HOME/cluster
  exit 0
fi