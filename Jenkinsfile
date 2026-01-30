pipeline {
    agent {label'docker-agent'}

    environment {
        IMAGE_NAME = "manishagawade/blog-app:latest"
        CONTAINER_NAME = "simple-blog"
        GITHUB_REPO = "https://github.com/GitGawade/CI-CD-Project.git"
        SCANNER_HOME = tool 'sonar'   // Name of SonarQube Scanner in Jenkins tools
    }

    stages {

        stage('Clone Repository') {
            steps {
                withCredentials([string(credentialsId: 'github', variable: 'GITHUB_TOKEN')]) {
                    sh '''
                    rm -rf app
                    git clone https://${GITHUB_TOKEN}@github.com/GitGawade/CI-CD-Project.git app
                    '''
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('sonar') {   // SonarQube server name
                    sh """
                    cd app
                    ${SCANNER_HOME}/bin/sonar-scanner \
                      -Dsonar.projectKey=blog-app \
                      -Dsonar.projectName=blog-app \
                      -Dsonar.sources=.
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
                cd app
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
                sleep 7
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
