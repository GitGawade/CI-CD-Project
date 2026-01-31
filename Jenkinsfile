pipeline {
    agent { label 'docker-agent' }

    environment {
        IMAGE_NAME      = "manishagawade/blog-app"
        IMAGE_TAG       = "latest"
        SONAR_HOST      = "http://13.127.66.96:9000"
    }

    stages {
        stage('Clean Workspace') {
            steps {
                cleanWs()
            }
        }

        stage('Git Clone') {
            steps {
                sh '''
                    echo "Cloning repository..."
                    git clone https://github.com/GitGawade/CI-CD-Project.git .
                    git status
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo "Running SonarQube analysis..."
                script {
                    withCredentials([string(credentialsId: 'sonar', variable: 'SONAR_TOKEN')]) {
                        sh """
                            docker run --rm \
                                -e SONAR_HOST_URL="${SONAR_HOST}" \
                                -e SONAR_LOGIN="${SONAR_TOKEN}" \
                                -v "${PWD}:/usr/src" \
                                -w /usr/src \
                                sonarsource/sonar-scanner-cli:latest \
                                sonar-scanner \
                                -Dsonar.projectKey=blog-app \
                                -Dsonar.projectName=blog-app \
                                -Dsonar.sources=. \
                                -Dsonar.host.url=${SONAR_HOST} \
                                -Dsonar.login=${SONAR_TOKEN}
                        """
                    }
                }
            }
        }

        stage('Trivy FS Scan') {
            steps {
                echo "Scanning source code..."
                sh '''
                    docker run --rm \
                        -v $(pwd):/src \
                        aquasec/trivy:latest \
                        fs --exit-code 0 --severity HIGH,CRITICAL /src
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image..."
                sh '''
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                '''
            }
        }

        stage('Trivy Image Scan') {
            steps {
                echo "Scanning Docker image..."
                sh '''
                    docker run --rm \
                        aquasec/trivy:latest \
                        image --exit-code 0 --severity HIGH,CRITICAL ${IMAGE_NAME}:${IMAGE_TAG}
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                echo "Pushing to Docker Hub..."
                script {
                    withCredentials([usernamePassword(
                        credentialsId: 'dockerhub',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )]) {
                        sh """
                            echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin
                            docker push ${IMAGE_NAME}:${IMAGE_TAG}
                        """
                    }
                }
            }
        }

        stage('Deploy Container') {
            steps {
                echo "Deploying..."
                sh '''
                    docker rm -f blog-app || true
                    docker run -d -p 5000:5000 --name blog-app ${IMAGE_NAME}:${IMAGE_TAG}
                    echo "Deployment process completed"
                '''
            }
        }

        stage('Health Check') {
            steps {
                echo "Checking health..."
                sh '''
                    sleep 5
                    docker ps | grep blog-app
                '''
            }
        }
    }

    post {
        always {
            echo "Pipeline completed"
            sh '''
                echo "Cleaning up..."
                docker rm -f blog-app || true
            '''
        }
        success {
            echo "Pipeline succeeded"
        }
        failure {
            echo "Pipeline failed"
        }
    }
}
