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

        stage('Checkout') {
            steps {
                echo "Cloning repository..."
                git branch: 'main', url: 'https://github.com/GitGawade/CI-CD-Project.git'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo "Running SonarQube analysis..."
                script {
                    withCredentials([string(credentialsId: 'sonar', variable: 'SONAR_TOKEN')]) {
                        sh """
                            sudo docker run --rm \
                                -e SONAR_HOST_URL="${SONAR_HOST}" \
                                -e SONAR_LOGIN="${SONAR_TOKEN}" \
                                -v "${PWD}:/usr/src" \
                                -w /usr/src \
                                sonarsource/sonar-scanner-cli:latest \
                                sonar-scanner \
                                -Dsonar.projectKey=flask_blog \
                                -Dsonar.projectName=flask_blog \
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
                sh """
                    sudo docker run --rm \
                        -v $(pwd):/src \
                        aquasec/trivy:latest \
                        fs --exit-code 0 --severity HIGH,CRITICAL /src
                """
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image..."
                sh """
                    sudo docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                """
            }
        }

        stage('Trivy Image Scan') {
            steps {
                echo "Scanning Docker image..."
                sh """
                    sudo docker run --rm \
                        aquasec/trivy:latest \
                        image --exit-code 0 --severity HIGH,CRITICAL ${IMAGE_NAME}:${IMAGE_TAG}
                """
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
                            echo "${DOCKER_PASS}" | sudo docker login -u "${DOCKER_USER}" --password-stdin
                            sudo docker push ${IMAGE_NAME}:${IMAGE_TAG}
                        """
                    }
                }
            }
        }

        stage('Deploy Container') {
            steps {
                echo "Deploying..."
                sh """
                    sudo docker rm -f blog-app || true
                    sudo docker run -d -p 5000:5000 --name blog-app ${IMAGE_NAME}:${IMAGE_TAG}
                    echo "Deployment process completed"
                """
            }
        }

        stage('Health Check') {
            steps {
                echo "Checking health..."
                sh """
                    sleep 5
                    sudo docker ps | grep blog-app
                """
            }
        }
    }

    post {
        always {
            echo "Pipeline completed"
            sh """
                echo "Cleaning up..."
                sudo docker rm -f blog-app || true
            """
        }
        success {
            echo "Pipeline succeeded"
        }
        failure {
            echo "Pipeline failed"
        }
    }
}
