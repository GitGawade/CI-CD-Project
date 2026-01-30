pipeline {
    agent { label 'docker-agent' }

    environment {
        IMAGE_NAME      = "manishagawade/blog-app"
        IMAGE_TAG       = "latest"
        CONTAINER_NAME  = "blog-app"
        GIT_REPO        = "https://github.com/GitGawade/CI-CD-Project.git"
        SONAR_HOST      = "http://13.127.66.96:9000"  // SonarQube server
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Cloning repository..."
                // Ensure Git is installed on Jenkins agent
                sh 'git --version || apt update && apt install -y git'
                git branch: 'main', url: "${GIT_REPO}"
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo "Running SonarQube analysis using Docker..."
                withCredentials([string(credentialsId: 'sonar', variable: 'SONAR_TOKEN')]) {
                    script {
                        docker.image('sonarsource/sonar-scanner-cli:latest').inside {
                            sh """
                              sonar-scanner \
                              -Dsonar.projectKey=blog-app \
                              -Dsonar.projectName=blog-app \
                              -Dsonar.sources=. \
                              -Dsonar.host.url=$SONAR_HOST \
                              -Dsonar.login=$SONAR_TOKEN
                            """
                        }
                    }
                }
            }
        }

        stage('SonarQube Quality Gate') {
            steps {
                echo "Checking SonarQube Quality Gate..."
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Trivy FS Scan (Source Code)') {
            steps {
                echo "Scanning source code with Trivy..."
                script {
                    docker.image('aquasec/trivy:latest').inside {
                        sh 'trivy fs --exit-code 1 --severity HIGH,CRITICAL .'
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image..."
                sh 'docker build -t $IMAGE_NAME:$IMAGE_TAG .'
            }
        }

        stage('Trivy Image Scan') {
            steps {
                echo "Scanning Docker image with Trivy..."
                sh 'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image --exit-code 1 --severity HIGH,CRITICAL $IMAGE_NAME:$IMAGE_TAG'
            }
        }

        stage('Push Docker Image') {
            steps {
                echo "Pushing Docker image to Docker Hub..."
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh """
                      echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                      docker push $IMAGE_NAME:$IMAGE_TAG
                    """
                }
            }
        }

        stage('Deploy Container') {
            steps {
                echo "Deploying container..."
                sh """
                  docker rm -f $CONTAINER_NAME || true
                  docker run -d -p 5000:5000 --name $CONTAINER_NAME $IMAGE_NAME:$IMAGE_TAG
                """
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished'
        }
        success {
            echo 'Build, scan, push, and deployment completed successfully'
        }
        failure {
            echo 'Pipeline failed. Check logs above.'
        }
    }
}
