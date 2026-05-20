// ─────────────────────────────────────────────────────────────────────────────
// Jenkinsfile — mirrors .github/workflows/ci-cd.yml
// Stages: Quality → Test → Docker Build/Push → Trivy Scan
// Runs on: main, develop branches
// ─────────────────────────────────────────────────────────────────────────────

pipeline {
    agent any

    environment {
        PYTHON_VERSION  = '3.9'
        IMAGE_NAME      = "crud-api"
        // Jenkins credentials IDs (configure in Jenkins → Manage Credentials)
        DOCKERHUB_CREDS = credentials('dockerhub-credentials')   // username/password binding
    }

    // Only run on main and develop branches
    triggers {
        githubPush()
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
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
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
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            environment {
                DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/crud_db_test'
            }
            steps {
                echo '── Starting PostgreSQL container ──'
                sh '''
                    docker run -d \
                        --name postgres-test-${BUILD_NUMBER} \
                        --network host \
                        -e POSTGRES_USER=postgres \
                        -e POSTGRES_PASSWORD=postgres \
                        -e POSTGRES_DB=crud_db_test \
                        postgres:15

                    # Wait for postgres to be ready
                    echo "Waiting for PostgreSQL..."
                    for i in $(seq 1 30); do
                        docker exec postgres-test-${BUILD_NUMBER} pg_isready -U postgres && break
                        sleep 2
                    done
                '''

                echo '── Installing Python dependencies ──'
                sh 'pip install --quiet -r requirements.txt pytest pytest-cov httpx'

                echo '── Running tests with coverage ──'
                sh 'pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=xml'
            }
            post {
                always {
                    echo '── Stopping PostgreSQL container ──'
                    sh 'docker stop postgres-test-${BUILD_NUMBER} && docker rm postgres-test-${BUILD_NUMBER} || true'

                    // Archive coverage report
                    archiveArtifacts artifacts: 'coverage.xml', allowEmptyArchive: true

                    // Publish JUnit-style test results if you use pytest-junit
                    // junit 'test-results/*.xml'
                }
            }
        }

        // ─────────────────────────────────────────────
        // 3. Docker Build & Push to Docker Hub
        // ─────────────────────────────────────────────
        stage('3 · Docker Build & Push') {
            when {
                allOf {
                    branch 'main'
                    not { changeRequest() }   // skip on PRs
                }
            }
            steps {
                echo '── Logging in to Docker Hub ──'
                sh 'echo $DOCKERHUB_CREDS_PSW | docker login -u $DOCKERHUB_CREDS_USR --password-stdin'

                echo '── Building Docker image ──'
                sh '''
                    docker build -t $DOCKERHUB_CREDS_USR/${IMAGE_NAME}:latest \
                                 -t $DOCKERHUB_CREDS_USR/${IMAGE_NAME}:${GIT_COMMIT:0:7} \
                                 .
                '''

                echo '── Pushing image to Docker Hub ──'
                sh '''
                    docker push $DOCKERHUB_CREDS_USR/${IMAGE_NAME}:latest
                    docker push $DOCKERHUB_CREDS_USR/${IMAGE_NAME}:${GIT_COMMIT:0:7}
                    echo "✅ Pushed: $DOCKERHUB_CREDS_USR/${IMAGE_NAME}:latest"
                    echo "✅ Pushed: $DOCKERHUB_CREDS_USR/${IMAGE_NAME}:sha-${GIT_COMMIT:0:7}"
                '''
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
            when {
                allOf {
                    branch 'main'
                    not { changeRequest() }   // skip on PRs
                }
            }
            steps {
                echo '── Pulling image for scan ──'
                sh 'docker pull $DOCKERHUB_CREDS_USR/${IMAGE_NAME}:latest'

                echo '── Running Trivy scan (table output) ──'
                sh '''
                    docker run --rm \
                        -v /var/run/docker.sock:/var/run/docker.sock \
                        -v $HOME/.cache/trivy:/root/.cache/trivy \
                        aquasec/trivy:latest image \
                        --severity CRITICAL,HIGH \
                        --ignore-unfixed \
                        --exit-code 1 \
                        $DOCKERHUB_CREDS_USR/${IMAGE_NAME}:latest
                '''

                echo '── Running Trivy scan (JSON report) ──'
                sh '''
                    docker run --rm \
                        -v /var/run/docker.sock:/var/run/docker.sock \
                        -v $HOME/.cache/trivy:/root/.cache/trivy \
                        aquasec/trivy:latest image \
                        --severity CRITICAL,HIGH \
                        --ignore-unfixed \
                        --format json \
                        --output trivy-results.json \
                        $DOCKERHUB_CREDS_USR/${IMAGE_NAME}:latest || true
                '''
            }
            post {
                always {
                    // Archive the Trivy JSON report as a build artifact
                    archiveArtifacts artifacts: 'trivy-results.json', allowEmptyArchive: true
                    echo '── Trivy scan complete. Report archived. ──'
                }
            }
        }
    }

    // ─────────────────────────────────────────────
    // Post-pipeline notifications
    // ─────────────────────────────────────────────
    post {
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline FAILED. Check the logs above.'
        }
        always {
            // Clean up any dangling test containers just in case
            sh 'docker ps -aq --filter "name=postgres-test-${BUILD_NUMBER}" | xargs docker rm -f 2>/dev/null || true'
            cleanWs()   // wipe workspace after every build
        }
    }
}
