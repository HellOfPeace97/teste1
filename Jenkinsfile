pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'docker build . -t tppd24/backend'
            }
        }
        stage('Push Images') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'docker_username', passwordVariable: 'docker_password')]) {
                        sh "docker login https://index.docker.io/v1/ --username \"\$docker_username\" --password \"\$docker_password\""
                    }
                    sh 'docker push tppd24/backend'
                }
            }
        }
        // Additional stages like testing, deployment can be added here
    }

    post {
        success {
            emailext(
                subject: "SUCCESS: Docker Image Build and Push #${BUILD_NUMBER}",
                body: "The Docker image build and push was successful. Great job!",
                to: 'tppd24@gmail.com'
            )
        }
        failure {
            emailext(
                subject: "FAILURE: Docker Image Build and Push #${BUILD_NUMBER}",
                body: "The Docker image build and push failed. Please check the Jenkins console output at ${BUILD_URL} to see the details.",
                to: 'tppd24@gmail.com'
            )
        }
        unstable {
            emailext(
                subject: "UNSTABLE: Docker Image Build and Push #${BUILD_NUMBER}",
                body: "The build is unstable. There might be some issues that require attention.",
                to: 'tppd24@gmail.com'
            )
        }
        aborted {
            emailext(
                subject: "ABORTED: Docker Image Build and Push #${BUILD_NUMBER}",
                body: "The Docker image build and push was aborted. Please check with your team.",
                to: 'tppd24@gmail.com'
            )
        }
    }
}
