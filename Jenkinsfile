pipeline {
    agent any

    environment {
        APP_IMAGE_NAME = "cloudops-e2e-app"
        TEST_IMAGE_NAME = "cloudops-selenium-runner"
        BUILD_TAG = "${env.BUILD_NUMBER}"
        STAGING_PORT = "5000"
        REPORTS_DIR = "reports"
        // Remote VM Configuration (Configure these credentials in Jenkins)
        TARGET_VM_HOST = credentials('TARGET_VM_HOST') // e.g. 192.168.1.100 or ec2-xx.compute.amazonaws.com
        TARGET_VM_USER = "ubuntu"
        SSH_KEY_CREDENTIAL_ID = "vm-ssh-private-key"
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '15'))
        timestamps()
        ansiColor('xterm')
    }

    stages {
        stage('Checkout & Lint') {
            steps {
                echo "=== Step 1: Checking out code and validating syntax ==="
                sh '''
                    python3 -m py_compile app/app.py
                    echo "Syntax validation passed!"
                '''
            }
        }

        stage('Build Docker Images') {
            steps {
                echo "=== Step 2: Building Application & Selenium Runner Containers ==="
                sh '''
                    docker build -t ${APP_IMAGE_NAME}:${BUILD_TAG} -t ${APP_IMAGE_NAME}:latest -f Dockerfile .
                    docker build -t ${TEST_IMAGE_NAME}:${BUILD_TAG} -f Dockerfile.test .
                '''
            }
        }

        stage('Ephemeral Environment Setup') {
            steps {
                echo "=== Step 3: Launching Ephemeral Test Environment ==="
                sh '''
                    # Clean up old test containers if any
                    docker rm -f devops_web_app_ci || true
                    docker network create e2e-ci-network || true

                    # Start target app container on test network
                    docker run -d --name devops_web_app_ci \
                        --network e2e-ci-network \
                        -e SECRET_KEY="ci-test-secret" \
                        ${APP_IMAGE_NAME}:${BUILD_TAG}

                    # Wait for app healthcheck
                    echo "Waiting for app service to become healthy..."
                    sleep 5
                '''
            }
        }

        stage('Execute Selenium E2E Tests') {
            steps {
                echo "=== Step 4: Running Headless Selenium Automated Tests ==="
                sh '''
                    mkdir -p ${REPORTS_DIR}/screenshots

                    # Run Selenium test runner container targeting the ephemeral app
                    docker run --rm \
                        --network e2e-ci-network \
                        -e APP_BASE_URL="http://devops_web_app_ci:5000" \
                        -v $(pwd)/${REPORTS_DIR}:/workspace/reports \
                        ${TEST_IMAGE_NAME}:${BUILD_TAG} \
                        pytest tests/ -v --headless \
                        --html=/workspace/reports/e2e_report.html \
                        --junitxml=/workspace/reports/junit_results.xml \
                        --self-contained-html
                '''
            }
        }

        stage('Quality Gate & Publish Reports') {
            steps {
                echo "=== Step 5: Archiving Reports and Publishing Test Results ==="
                // Publish JUnit XML test results
                junit allowEmptyResults: true, testResults: 'reports/junit_results.xml'

                // Publish HTML report
                publishHTML([
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: 'e2e_report.html',
                    reportName: 'Selenium E2E Test Report',
                    reportTitles: 'E2E Selenium Automation Results'
                ])

                // Archive failure screenshots if any
                archiveArtifacts allowEmptyArchive: true, artifacts: 'reports/screenshots/*.png'
            }
        }

        stage('Deploy to Target VM') {
            when {
                branch 'main'
            }
            steps {
                echo "=== Step 6: Deploying Verified Container to Target Virtual Machine ==="
                sshagent([SSH_KEY_CREDENTIAL_ID]) {
                    sh '''
                        echo "Deploying to target VM: ${TARGET_VM_USER}@${TARGET_VM_HOST}"

                        # 1. Transfer docker-compose or compose definition to VM
                        scp -o StrictHostKeyChecking=no docker-compose.yml ${TARGET_VM_USER}@${TARGET_VM_HOST}:/home/${TARGET_VM_USER}/app/docker-compose.yml

                        # 2. Trigger remote container pull/run on VM
                        ssh -o StrictHostKeyChecking=no ${TARGET_VM_USER}@${TARGET_VM_HOST} "
                            cd /home/${TARGET_VM_USER}/app && \
                            docker compose pull web-app || docker run -d --restart always -p 5000:5000 --name cloudops-prod-app ${APP_IMAGE_NAME}:${BUILD_TAG} && \
                            echo 'Application successfully deployed on target VM!'
                        "
                    '''
                }
            }
        }
    }

    post {
        always {
            echo "=== Cleaning Up Ephemeral CI Resources ==="
            sh '''
                docker rm -f devops_web_app_ci || true
                docker network rm e2e-ci-network || true
            '''
        }
        success {
            echo "Pipeline succeeded! All Selenium E2E tests passed and deployment completed."
        }
        failure {
            echo "Pipeline failed! Inspect Selenium report and failure screenshots in Jenkins artifacts."
        }
    }
}
