#!/bin/bash

instance_size=${1:-m6i.2xlarge}
region=${2:-us-east-2}

aws_access_key_id=${AWS_ACCESS_KEY_ID}
aws_secret_access_key=${AWS_SECRET_ACCESS_KEY}
aws_region=${AWS_REGION}
base_domain=${BASE_DOMAIN:-example.com}
cluster_name=${CLUSTER_NAME:-test-cluster}
pull_secret_file=${PULL_SECRET_FILE}

print_aws_variables() {
    echo "Export the following AWS variables before running this script:"
    echo "export AWS_ACCESS_KEY_ID=\"YOUR_ACCESS_KEY_ID\""
    echo "export AWS_SECRET_ACCESS_KEY=\"YOUR_SECRET_ACCESS_KEY\""
    echo "export AWS_REGION=\"YOUR_AWS_REGION\""
}

print_pull_secret_variable() {
    echo "Export the following variable before running this script:"
    echo "export PULL_SECRET_FILE=\"/path/to/your/pull-secret.json\""
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

# Check if Pull Secret is provided
if [ -z ${pull_secret_file} ]; then
    echo "PULL_SECRET_FILE is not set"
    print_pull_secret_variable
    exit 1
elif [ ! -f ${pull_secret_file} ]; then
    echo "PULL_SECRET_FILE does not point to a valid file"
    exit 1
fi

# Read the pull secret content
pull_secret=$(cat ${pull_secret_file})

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
  curl -OL https://raw.githubusercontent.com/tosin2013/openshift-4-deployment-notes/master/pre-steps/configure-openshift-packages.sh
  chmod +x configure-openshift-packages.sh
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
mkdir -p $HOME/cluster
cat <<EOF > $HOME/cluster/install-config.yaml
apiVersion: v1
baseDomain: ${base_domain}
compute:
- hyperthreading: Enabled
  name: worker
  platform:
    aws:
      rootVolume:
        iops: 2000
        size: 500
        type: io1
      type: ${instance_size}
  replicas: 3
controlPlane:
  hyperthreading: Enabled
  name: master
  platform: {}
  replicas: 3
metadata:
  name: ${cluster_name}
platform:
  aws:
    region: ${region}
pullSecret: '${pull_secret}'
sshKey: '$(cat /home/$USER/.ssh/cluster-key.pub)'
EOF

# Create the cluster with standard workers
yes | openshift-install create cluster --dir=$HOME/cluster --log-level debug

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

# Check if the --destroy flag is passed
if [ "$3" == "--destroy" ]; then
  echo "Destroying the cluster and deleting the $HOME/cluster folder..."
  openshift-install destroy cluster --dir=$HOME/cluster --log-level debug
  rm -rf $HOME/cluster
  exit 0
fi
