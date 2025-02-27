# Route53 DNS Monitor

A Python-based monitoring system that tracks changes in AWS Route53 DNS records and sends notifications to Slack.

## Installation

### Option 1: Using pip with requirements.txt
```bash
# Clone the repository
git clone https://github.com/vaibhavkubade/route53-monitor.git
cd route53-monitor

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Using setup.py (Development Mode)
```bash
# Clone the repository
git clone https://github.com/vaibhavkubade/route53-monitor.git
cd route53-monitor

# Install in development mode
pip install -e .
```

This will install the package in development mode and create a command-line entry point:
```bash
route53-monitor --test  # Test Slack integration
route53-monitor        # Run single scan
route53-monitor --loop # Run continuous monitoring
```

## Configuration

### Jenkins Setup

1. Create a new Jenkins Pipeline
2. Configure the Slack webhook credential:
   - Go to Jenkins > Credentials > System
   - Add new credential
   - Kind: Secret text
   - ID: slack-webhook-url
   - Secret: Your Slack webhook URL

3. Set up the pipeline using the provided Jenkinsfile

### AWS IAM Setup

1. Create an IAM role with Route53 read permissions

Required IAM Policy:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "route53:ListHostedZones",
                "route53:ListResourceRecordSets"
            ],
            "Resource": "*"
        }
    ]
}
```

2. Attach the role to your Jenkins instance

For different Jenkins environments:
- EC2: Attach the IAM role directly to the EC2 instance
- ECS/EKS: Use service account/IAM role for the container
- Other environments: Use AWS credentials provider plugin with assumed role

No AWS access keys are required as the script uses IAM role-based authentication.

## Usage

### Manual Testing

Test Slack integration:
```bash:readme.md
python3 route53_monitor.py --test
```

Run a manual scan:
```bash
python3 route53_monitor.py
```

Run continuous monitoring (3-second intervals):
```bash
python3 route53_monitor.py --loop
```

### Jenkins Pipeline

The pipeline will:
- Run every 12 hours (at 00:00 and 12:00)
- Install dependencies
- Execute the monitor
- Archive logs
- Send failure notifications

## File Structure

```
.
├── route53_monitor.py     # Main monitoring script
├── Jenkinsfile           # Jenkins pipeline configuration
├── .env                  # Environment variables
├── previous_route53_scan.json  # State file for change detection
├── route53_monitor.log   # Application logs
└── last_run.txt         # Timestamp of last execution
```

## Notifications

The monitor sends Slack notifications for:
- 🟢 Added DNS records
- 🟡 Modified DNS records
- 🔴 Deleted DNS records
- ❌ Monitoring failures

## Logging

Logs are stored in `route53_monitor.log` with the following information:
- Timestamp
- Process ID
- Log level
- Detailed messages about operations and changes

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Authors

- Vaibhav Kubade

## Support

For support, please open an issue in the repository or contact dev.vaibhavk@google.com
