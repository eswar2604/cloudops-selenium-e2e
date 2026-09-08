#!/usr/bin/env bash
# ==============================================================================
# Target VM Provisioning Script (Ubuntu / Debian)
# Sets up Docker, Docker Compose, Python, and Google Chrome for E2E Testing
# ==============================================================================
set -euo pipefail

echo "========================================================="
echo " Starting Target VM Provisioning for CI/CD & Testing"
echo "========================================================="

# 1. Update system packages
echo "--> Updating APT package index..."
sudo apt-get update -y
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release git python3 python3-pip

# 2. Install Docker & Docker Compose
echo "--> Installing Docker Engine..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker "$USER"
    rm get-docker.sh
    echo "Docker installed successfully."
else
    echo "Docker is already installed."
fi

# 3. Install Docker Compose plugin
sudo apt-get install -y docker-compose-plugin

# 4. Optional: Install Google Chrome and ChromeDriver for native VM testing
echo "--> Installing Google Chrome for headless E2E testing..."
if ! command -v google-chrome &> /dev/null; then
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo apt install -y ./google-chrome-stable_current_amd64.deb || sudo apt-get -f install -y
    rm google-chrome-stable_current_amd64.deb
    echo "Google Chrome installed."
else
    echo "Google Chrome is already installed."
fi

# 5. Create application directory
mkdir -p ~/app/reports

echo "========================================================="
echo " VM Provisioning Complete!"
echo " Log out and log back in to apply Docker group permissions."
echo "========================================================="
