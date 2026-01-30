pipeline {
    agent { label 'docker-agent' }

    environment {
        IMAGE_NAME = "manishagawade/blog-app:latest"
        CONTAINER_NAME = "simple-blog"
        GITHUB_REPO = "https://github.com/GitGawade/CI-CD-Project.git"
        SCANNER_HOME = tool 'sonar'
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main', url: "${GITHUB_REPO}"
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('sonar') {
                    sh """
                    ${SCANNER_HOME}/bin/sonar-scanner \
                      -Dsonar.projectKey=blog-app \
                      -Dsonar.projectName=blog-app \
                      -Dsonar.sources=. \
                      -Dsonar.host.url=$SONAR_HOST_URL \
                      -Dsonar.login=$SONAR_AUTH_TOKEN
                    """
                }
            }
        }

        stage('SonarQube Quality Gate') {
            steps {
                script {
                    timeout(time: 2, unit: 'MINUTES') {
                        waitForQualityGate abortPipeline: true
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                docker build -t $IMAGE_NAME .
                '''
            }
        }

        stage('Trivy Image Scan') {
            steps {
                sh '''
                docker run --rm \
                  -v /var/run/docker.sock:/var/run/docker.sock \
                  aquasec/trivy image --severity HIGH,CRITICAL $IMAGE_NAME
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

        stage('Run New Container with Volume') {
            steps {
                sh '''
                docker rm -f $CONTAINER_NAME || true
                mkdir -p $WORKSPACE/data
                docker run -d -p 5000:5000 \
                  -v $WORKSPACE/data:/app/data \
                  --name $CONTAINER_NAME \
                  $IMAGE_NAME
                '''
            }
        }

        stage('OWASP ZAP Scan') {
            steps {
                sh '''
                docker run --rm --network host -u root \
                  -v $(pwd):/zap/wrk/:rw \
                  zaproxy/zap-stable \
                  zap-baseline.py \
                  -t http://localhost:5000 \
                  -r zap-report.html || true
                '''
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished'
        }
        success {
            echo 'Build, scan, and deployment completed'
        }
        failure {
            echo 'Pipeline failed due to build/deploy issue (NOT security scans)'
        }
    }
}
