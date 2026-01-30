pipeline {
    agent { label 'docker-agent' }

    environment {
        IMAGE_NAME      = "manishagawade/blog-app"
        IMAGE_TAG       = "latest"
        GIT_REPO        = "https://github.com/GitGawade/CI-CD-Project.git"
        CONTAINER_NAME  = "blog-container"
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
                withSonarQubeEnv('sonar') {
                    withCredentials([string(credentialsId: 'sonar', variable: 'SONAR_TOKEN')]) {
                        sh '''
                          sonar-scanner \
                          -Dsonar.projectKey=blog-app \
                          -Dsonar.projectName=blog-app \
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

        stage('Trivy Scan (Source Code)') {
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
