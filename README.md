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
2. Attach the role to your Jenkins instance

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
- Run automatically every minute
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

For support, please open an issue in the repository or contact vaibhav.kubade@juspay.in
