pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "manishagawade/blog-app:latest"
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
                docker build -t $DOCKER_IMAGE .
                '''
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                    echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                    '''
                }
            }
        }

        stage('Push Image to Docker Hub') {
            steps {
                sh 'docker push $DOCKER_IMAGE'
            }
        }

        stage('Stop Old Container') {
            steps {
                sh 'docker rm -f simple-blog || true'
            }
        }

        stage('Run New Container with Volume') {
            steps {
                sh '''
                mkdir -p $WORKSPACE/data
                docker run -d \
                  -p 5000:5000 \
                  -v $WORKSPACE/data:/app/data \
                  --name simple-blog \
                  $DOCKER_IMAGE
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh 'docker ps | grep simple-blog'
            }
        }
    }

    post {
        success {
            echo 'Image pushed to Docker Hub & app deployed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check Jenkins logs.'
        }
    }
}
