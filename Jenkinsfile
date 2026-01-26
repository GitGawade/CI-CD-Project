pipeline {
    agent any

    tools {
        sonarRunner 'sonar'
    }

    environment {
        IMAGE_NAME = "manishagawade/blog-app:latest"
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

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('sonar') {
                    sh '''
                    cd app
                    sonar-scanner \
                      -Dsonar.projectKey=blog-app \
                      -Dsonar.projectName=blog-app \
                      -Dsonar.sources=.
                    '''
                }
            }
        }

        stage('SonarQube Quality Gate (Non Blocking)') {
            steps {
                script {
                    timeout(time: 2, unit: 'MINUTES') {
                        waitForQualityGate abortPipeline: false
                    }
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

        stage('Trivy Image Scan (Non Blocking)') {
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

        stage('OWASP ZAP Scan (Non Blocking)') {
            steps {
                sh '''
                docker run --rm --network host -u root \
                  -v $(pwd):/zap/wrk/:rw \
                  zaproxy/zap-stable \
                  zap-baseline.py \
                  -t http://192.168.80.25:5000 \
                  -r zap-report.html || true
                '''
            }
        }
    }

    post {
        always {
            publishHTML(target: [
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: '.',
                reportFiles: 'zap-report.html',
                reportName: 'OWASP ZAP Security Report'
            ])
        }

        success {
            echo 'Pipeline completed successfully'
        }

        failure {
            echo 'Pipeline failed due to build/deploy issue (NOT security scans)'
        }
    }
}
