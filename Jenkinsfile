pipeline {
    // Run all stages on the docker-agent
    agent { label 'docker-agent' }

    environment {
        IMAGE_NAME = sanjana038/blog-app"
        IMAGE_TAG = "latest"
        SONAR_HOME = tool "sonar"
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/GitGawade/CI-CD-Project.git'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv("sonar") {
                    sh """
                      $SONAR_HOME/bin/sonar-scanner \
                      -Dsonar.projectName=flask_blog \
                      -Dsonar.projectKey=flask_blog
                    """
                }
            }
        }

        stage('SonarQube Quality Gate') {
    steps {
        sleep 5 // Give SonarQube a moment to process
        timeout(time: 5, unit: 'MINUTES') {
            waitForQualityGate abortPipeline: true
        }
    }
}

        stage('Trivy FS Scan (Source Code)') {
            steps {
                sh '''
                  trivy fs \
                  --exit-code 1 \
                  --severity HIGH,CRITICAL \
                  .
                '''
            }
        }

        stage('Build Image') {
            steps {
                sh 'docker build -t $IMAGE_NAME:$IMAGE_TAG .'
            }
        }

        stage('Trivy Image Scan') {
            steps {
                sh '''
                  trivy image \
                  --exit-code 0 \
                  --severity HIGH,CRITICAL \
                  $IMAGE_NAME:$IMAGE_TAG
                '''
            }
        }

        stage('Push Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                      echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                      docker push $IMAGE_NAME:$IMAGE_TAG
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                  docker compose pull
                  docker compose up -d --force-recreate
                '''
            }
        }
    }
}