pipeline {
    agent any
    
    environment {
        SLACK_WEBHOOK_URL = credentials('slack-webhook-url')
    }
    
    triggers {
        // Run every minute
        cron('* * * * *')
    }
    
    stages {
        stage('Setup') {
            steps {
                sh '''
                    python3 -m pip install --user boto3 python-dotenv requests
                '''
            }
        }
        
        stage('Run Monitor') {
            steps {
                script {
                    // Create .env file with only Slack webhook
                    writeFile file: '.env', text: """
                        SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
                    """
                    
                    // Run the monitor script
                    sh 'python3 route53_monitor.py'
                }
            }
        }
    }
    
    post {
        always {
            // Archive logs
            archiveArtifacts artifacts: '*.log', allowEmptyArchive: true
        }
        failure {
            // Send notification on failure
            slackSend(
                color: 'danger',
                message: "Route53 Monitor Failed: ${env.BUILD_URL}"
            )
        }
    }
} 