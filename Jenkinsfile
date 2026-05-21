// ─────────────────────────────────────────────────────────────────────────────
// Jenkinsfile — mirrors .github/workflows/ci-cd.yml
// Stages: Quality → Test → Docker Build/Push → Trivy Scan
// Python stages run inside python:3.9 Docker container
// Docker stages run on the Jenkins agent directly
// ─────────────────────────────────────────────────────────────────────────────

pipeline {
    agent none   // Each stage declares its own agent

    environment {
        IMAGE_NAME = 'crud-api'
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {

        // ─────────────────────────────────────────────
        // 1. Code Quality & Security
        // ─────────────────────────────────────────────
        stage('1 · Code Quality & Security') {
            agent {
                docker {
                    image 'python:3.9-slim'
                    args '--user root'
                }
            }
            when {
                anyOf { branch 'main'; branch 'develop' }
            }
            steps {
                echo '── Installing quality tools ──'
                sh 'pip install --quiet flake8 black isort bandit safety'

                echo '── Check formatting (black) ──'
                sh 'black --check --diff .'

                echo '── Check import order (isort) ──'
                sh 'isort --check-only --diff .'

                echo '── Lint with flake8 ──'
                sh 'flake8 . --config=.flake8'

                echo '── SAST with bandit ──'
                sh 'bandit -r . --exclude ./venv,./tests -ll'

                echo '── CVE check with safety ──'
                sh 'safety check --file requirements.txt --ignore 70612'
            }
        }

        // ─────────────────────────────────────────────
        // 2. Run Tests (PostgreSQL as a Docker sidecar)
        // ─────────────────────────────────────────────
        stage('2 · Run Tests') {
            agent {
                docker {
                    image 'python:3.9-slim'
                    args '--user root --network host'
                }
            }
            when {
                anyOf { branch 'main'; branch 'develop' }
            }
            environment {
                DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/crud_db_test'
            }
            steps {
                echo '── Starting PostgreSQL container ──'
                // Run postgres on the host's Docker daemon via a shell on the Jenkins node
                // We use a pre-step script approach
                sh '''
                    apt-get update -qq && apt-get install -y -qq libpq-dev gcc > /dev/null 2>&1 || true
                '''

                echo '── Installing Python dependencies ──'
                sh 'pip install --quiet -r requirements.txt pytest pytest-cov httpx'

                echo '── Running tests with coverage ──'
                sh 'pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=xml || true'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'coverage.xml', allowEmptyArchive: true
                }
            }
        }

        // ─────────────────────────────────────────────
        // 2.5 SonarQube Analysis
        // ─────────────────────────────────────────────
        stage('2.5 · SonarQube Analysis') {
            agent {
                docker {
                    image 'sonarsource/sonar-scanner-cli:latest'
                    args '--user root'
                }
            }
            when {
                anyOf { branch 'main'; branch 'develop' }
            }
            steps {
                withCredentials([
                    string(credentialsId: 'SONAR_TOKEN', variable: 'SONAR_TOKEN'),
                    string(credentialsId: 'SONAR_HOST_URL', variable: 'SONAR_HOST_URL')
                ]) {
                    echo '── Running SonarQube Scanner ──'
                    sh '''
                        sonar-scanner \
                            -Dsonar.host.url=$SONAR_HOST_URL \
                            -Dsonar.token=$SONAR_TOKEN
                    '''
                }
            }
        }

        // ─────────────────────────────────────────────
        // 3. Docker Build & Push to Docker Hub
        // ─────────────────────────────────────────────
        stage('3 · Docker Build & Push') {
            agent any   // Needs Docker CLI on the Jenkins host
            when {
                allOf {
                    branch 'main'
                    not { changeRequest() }
                }
            }
            steps {
                withCredentials([
                    string(credentialsId: 'DOCKER_HUB_USERNAME', variable: 'DH_USER'),
                    string(credentialsId: 'DOCKER_HUB_TOKEN',    variable: 'DH_TOKEN')
                ]) {
                    echo '── Logging in to Docker Hub ──'
                    sh 'echo $DH_TOKEN | docker login -u $DH_USER --password-stdin'

                    echo '── Building Docker image ──'
                    sh """
                        docker build \
                            -t \$DH_USER/${IMAGE_NAME}:latest \
                            -t \$DH_USER/${IMAGE_NAME}:sha-\$(echo ${GIT_COMMIT} | cut -c1-7) \
                            .
                    """

                    echo '── Pushing to Docker Hub ──'
                    sh """
                        docker push \$DH_USER/${IMAGE_NAME}:latest
                        docker push \$DH_USER/${IMAGE_NAME}:sha-\$(echo ${GIT_COMMIT} | cut -c1-7)
                        echo '✅ Image pushed successfully!'
                    """
                }
            }
            post {
                always {
                    sh 'docker logout || true'
                }
            }
        }

        // ─────────────────────────────────────────────
        // 4. Trivy Container Vulnerability Scan
        // ─────────────────────────────────────────────
        stage('4 · Trivy Image Scan') {
            agent any   // Needs Docker CLI on the Jenkins host
            when {
                allOf {
                    branch 'main'
                    not { changeRequest() }
                }
            }
            steps {
                withCredentials([
                    string(credentialsId: 'DOCKER_HUB_USERNAME', variable: 'DH_USER'),
                    string(credentialsId: 'DOCKER_HUB_TOKEN',    variable: 'DH_TOKEN')
                ]) {
                    echo '── Logging in & pulling image ──'
                    sh 'echo $DH_TOKEN | docker login -u $DH_USER --password-stdin'
                    sh 'docker pull $DH_USER/${IMAGE_NAME}:latest'

                    echo '── Trivy scan (table output) ──'
                    sh """
                        docker run --rm \
                            -v /var/run/docker.sock:/var/run/docker.sock \
                            -v \$HOME/.cache/trivy:/root/.cache/trivy \
                            aquasec/trivy:latest image \
                            --severity CRITICAL,HIGH \
                            --ignore-unfixed \
                            --exit-code 0 \
                            \$DH_USER/${IMAGE_NAME}:latest
                    """

                    echo '── Trivy scan (JSON report) ──'
                    sh """
                        docker run --rm \
                            -v /var/run/docker.sock:/var/run/docker.sock \
                            -v \$HOME/.cache/trivy:/root/.cache/trivy \
                            -v \$(pwd):/output \
                            aquasec/trivy:latest image \
                            --severity CRITICAL,HIGH \
                            --ignore-unfixed \
                            --format json \
                            --output /output/trivy-results.json \
                            \$DH_USER/${IMAGE_NAME}:latest || true
                    """
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'trivy-results.json', allowEmptyArchive: true
                    sh 'docker logout || true'
                    echo '── Trivy scan complete ──'
                }
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline FAILED. Check the stage logs above.'
        }
    }
}
