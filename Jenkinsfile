pipeline {
    // Run all stages on the docker-agent
    agent { label 'docker-agent' }

    environment {
        IMAGE_NAME = "manishagawade/flask-blog"
        IMAGE_TAG  = "latest"
        GIT_REPO   = "https://github.com/GitGawade/CI-CD-Project.git"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Cloning repository..."
                git branch: 'main', url: "${GIT_REPO}"
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo "Running SonarQube analysis..."
                // Use the SonarQube credentials ID 'sonar' created for Manisha
                withSonarQubeEnv('sonar') {
                    withCredentials([string(credentialsId: 'sonar', variable: 'SONAR_TOKEN')]) {
                        sh '''
                          sonar-scanner \
                          -Dsonar.projectName=flask_blog \
                          -Dsonar.projectKey=flask_blog \
                          -Dsonar.sources=. \
                          -Dsonar.host.url=$SONAR_HOST_URL \
                          -Dsonar.login=$SONAR_TOKEN
                        '''
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
                sh '''
                  trivy fs --exit-code 1 --severity HIGH,CRITICAL .
                '''
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
                sh '''
                  trivy image --exit-code 1 --severity HIGH,CRITICAL $IMAGE_NAME:$IMAGE_TAG
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                echo "Pushing Docker image to Docker Hub..."
                // Use the Docker Hub credentials ID 'dockerhub' for Manisha
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                      echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                      docker push $IMAGE_NAME:$IMAGE_TAG
                    '''
                }
            }
        }

        stage('Deploy Container') {
            steps {
                echo "Deploying container using Docker Compose..."
                sh '''
                  docker compose pull
                  docker compose up -d --force-recreate
                '''
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
