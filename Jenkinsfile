pipeline {
    agent any

    environment {
        IMAGE_NAME = "blog-app:latest"
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
                docker build -t blog-app:latest .
                '''
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
                  blog-app:latest
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
            echo '✅ Deployment successful! App is live on port 5000.'
        }
        failure {
            echo '❌ Deployment failed. Check logs.'
        }
    }
}
