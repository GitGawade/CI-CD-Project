pipeline {
    agent any

    environment {
        IMAGE_NAME = "yourdockerhubusername/blog-app:latest"
        CONTAINER_NAME = "simple-blog"
        GITHUB_REPO = "https://github.com/GitGawade/CI-CD-Project.git"
    }

    stages {

        stage('Clone Repository') {
            steps {
                withCredentials([string(credentialsId: 'github-pat', variable: 'GITHUB_TOKEN')]) {
                    sh '''
                    rm -rf app
                    git clone https://${GITHUB_TOKEN}@github.com/GitGawade/CI-CD-Project.git app
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                cd app
                docker build -t $IMAGE_NAME .
                '''
            }
        }

        stage('Trivy Image Scan (Report Only)') {
            steps {
                sh '''
                docker run --rm \
                -v /var/run/docker.sock:/var/run/docker.sock \
                aquasec/trivy:latest image \
                --severity HIGH,CRITICAL \
                $IMAGE_NAME || true
                '''
            }
        }


        stage('Push Image to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                    echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                    docker push $IMAGE_NAME
                    '''
                }
            }
        }

        stage('Stop Old Container') {
            steps {
                sh 'docker rm -f $CONTAINER_NAME || true'
            }
        }

        stage('Run New Container with Volume') {
            steps {
                sh '''
                mkdir -p $WORKSPACE/data
                docker run -d \
                  -p 5000:5000 \
                  -v $WORKSPACE/data:/app/data \
                  --name $CONTAINER_NAME \
                  $IMAGE_NAME
                '''
            }
        }

        stage('OWASP ZAP Scan') {
            steps {
                sh '''
                docker run --rm \
                  -v $(pwd):/zap/wrk/:rw \
                  zaproxy/zap-stable \
                  zap-baseline.py \
                  -t http://localhost:5000 \
                  -r zap-report.html
                '''
            }
        }
    }

    post {
        always {
            publishHTML(target: [
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: '.',
                reportFiles: 'zap-report.html',
                reportName: 'OWASP ZAP Security Report'
            ])
        }

        success {
            echo ' CI/CD Pipeline completed successfully'
        }

        failure {
            echo ' Pipeline failed (Check Trivy or ZAP results)'
        }
    }
}
