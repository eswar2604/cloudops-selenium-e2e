#!/usr/bin/env bash
# ==============================================================================
# Helper Script: Deploy application container to a remote Target VM
# Usage: ./deploy_to_vm.sh <VM_USER> <VM_HOST> <IMAGE_TAG>
# ==============================================================================
set -euo pipefail

VM_USER="${1:-ubuntu}"
VM_HOST="${2:-localhost}"
IMAGE_TAG="${3:-latest}"

echo "========================================================="
echo " Deploying CloudOps Portal to Target VM"
echo " Host: ${VM_USER}@${VM_HOST}"
echo " Image Tag: ${IMAGE_TAG}"
echo "========================================================="

# 1. Copy docker-compose configuration
scp -o StrictHostKeyChecking=no docker-compose.yml "${VM_USER}@${VM_HOST}:~/app/docker-compose.yml"

# 2. Trigger container refresh on VM
ssh -o StrictHostKeyChecking=no "${VM_USER}@${VM_HOST}" bash -c "'
    cd ~/app
    # Stop old container if running
    docker stop cloudops-prod-app 2>/dev/null || true
    docker rm cloudops-prod-app 2>/dev/null || true

    # Run new release
    docker run -d \
        --name cloudops-prod-app \
        --restart unless-stopped \
        -p 5000:5000 \
        -e SECRET_KEY=\"prod-secret-token\" \
        cloudops-e2e-app:${IMAGE_TAG}

    echo \"Deployment status:\"
    docker ps --filter name=cloudops-prod-app
'"

echo "--> Deployment complete! Application is live at http://${VM_HOST}:5000"
