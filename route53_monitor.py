import boto3
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv
import requests
from typing import Dict, List, Any
import sys
import logging

# Define script directory first
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Load environment variables with correct path
load_dotenv(os.path.join(SCRIPT_DIR, '.env'))

# AWS credentials from .env
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')

# File paths
PREVIOUS_SCAN_FILE = os.path.join(SCRIPT_DIR, 'previous_route53_scan.json')
LOG_FILE = os.path.join(SCRIPT_DIR, 'route53_monitor.log')
LAST_RUN_FILE = os.path.join(SCRIPT_DIR, 'last_run.txt')

# Update logging configuration
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - PID:%(process)d - %(levelname)s - %(message)s'
)

class Route53Monitor:
    def __init__(self):
        self.route53_client = boto3.client('route53')

    def get_all_records(self) -> Dict[str, List[Dict[str, Any]]]:
        """Retrieve all Route 53 records from all hosted zones."""
        records = {}
        
        # Get all hosted zones
        paginator = self.route53_client.get_paginator('list_hosted_zones')
        for page in paginator.paginate():
            for zone in page['HostedZones']:
                zone_id = zone['Id']
                zone_name = zone['Name']
                records[zone_name] = []

                # Get records for each zone
                record_paginator = self.route53_client.get_paginator('list_resource_record_sets')
                for record_page in record_paginator.paginate(HostedZoneId=zone_id):
                    for record in record_page['ResourceRecordSets']:
                        records[zone_name].append({
                            'Name': record['Name'],
                            'Type': record['Type'],
                            'TTL': record.get('TTL', 0),
                            'ResourceRecords': record.get('ResourceRecords', []),
                            'AliasTarget': record.get('AliasTarget', None)
                        })

        return records

    def load_previous_scan(self) -> Dict:
        """Load previous scan results from file."""
        try:
            with open(PREVIOUS_SCAN_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_current_scan(self, records: Dict):
        """Save current scan results to file."""
        with open(PREVIOUS_SCAN_FILE, 'w') as f:
            json.dump(records, f, indent=2)

    def compare_records(self, previous: Dict, current: Dict) -> Dict:
        """Compare previous and current records to find changes."""
        changes = {
            'added': [],
            'deleted': [],
            'modified': []
        }
        
        logging.info(f"Comparing records - Previous zones: {list(previous.keys())}, Current zones: {list(current.keys())}")
        
        # Check for additions and modifications
        for zone_name, records in current.items():
            prev_zone_records = previous.get(zone_name, [])
            
            for record in records:
                matching_prev = next(
                    (r for r in prev_zone_records if r['Name'] == record['Name'] and r['Type'] == record['Type']),
                    None
                )
                
                if not matching_prev:
                    changes['added'].append({
                        'zone': zone_name,
                        'record': record
                    })
                elif matching_prev != record:
                    changes['modified'].append({
                        'zone': zone_name,
                        'old': matching_prev,
                        'new': record
                    })

        # Check for deletions
        for zone_name, records in previous.items():
            current_zone_records = current.get(zone_name, [])
            
            for record in records:
                if not any(r['Name'] == record['Name'] and r['Type'] == record['Type'] 
                          for r in current_zone_records):
                    changes['deleted'].append({
                        'zone': zone_name,
                        'record': record
                    })

        logging.info(f"Changes detected: Added={len(changes['added'])}, Modified={len(changes['modified'])}, Deleted={len(changes['deleted'])}")
        return changes

    def format_slack_message(self, changes: Dict) -> Dict:
        """Format changes for Slack notification."""
        total_changes = len(changes['added']) + len(changes['modified']) + len(changes['deleted'])
        
        blocks = [{
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🔄 Route 53 DNS Changes Detected ({total_changes} changes)"
            }
        }]

        if changes['added']:
            added_text = "\n".join([
                f"• Zone: {change['zone']}, Record: {change['record']['Name']} ({change['record']['Type']})"
                for change in changes['added']
            ])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🟢 Added Records:*\n{added_text}"
                }
            })

        if changes['modified']:
            modified_text = "\n".join([
                f"• Zone: {change['zone']}, Record: {change['new']['Name']} ({change['new']['Type']})"
                for change in changes['modified']
            ])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🟡 Modified Records:*\n{modified_text}"
                }
            })

        if changes['deleted']:
            deleted_text = "\n".join([
                f"• Zone: {change['zone']}, Record: {change['record']['Name']} ({change['record']['Type']})"
                for change in changes['deleted']
            ])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🔴 Deleted Records:*\n{deleted_text}"
                }
            })

        return {
            "blocks": blocks
        }

    def send_slack_notification(self, message: Dict):
        """Send notification to Slack."""
        try:
            logging.info(f"Attempting to send Slack notification: {message}")
            response = requests.post(
                SLACK_WEBHOOK_URL,
                json=message,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            logging.info("Slack notification sent successfully")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending Slack notification: {e}")
            print(f"Error sending Slack notification: {e}")

    def send_test_message(self):
        """Send a test message to Slack to verify the integration."""
        test_message = {
            "blocks": [{
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🧪 Route 53 Monitor - Test Message"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "This is a test message to verify the Slack integration is working correctly.\n*Time*: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }]
        }
        self.send_slack_notification(test_message)

def main():
    # Update timestamp file path
    with open(LAST_RUN_FILE, 'w') as f:
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    logging.info("Route53 Monitor started")
    monitor = Route53Monitor()
    try:
        # Check if test flag is provided
        if len(sys.argv) > 1 and sys.argv[1] == '--test':
            logging.info("Test flag detected, sending test message")
            print("Sending test message to Slack...")
            monitor.send_test_message()
            return
        
        # Get current records
        current_records = monitor.get_all_records()
        logging.info(f"Retrieved {sum(len(records) for records in current_records.values())} current records")
        
        # Load previous records
        previous_records = monitor.load_previous_scan()
        logging.info(f"Loaded {sum(len(records) for records in previous_records.values())} previous records")
        
        # Compare records
        changes = monitor.compare_records(previous_records, current_records)
        
        # If changes detected, send Slack notification
        if any(changes.values()):
            logging.info("Changes detected, preparing Slack message")
            slack_message = monitor.format_slack_message(changes)
            monitor.send_slack_notification(slack_message)
        else:
            logging.info("No changes detected")
        
        # Save current scan
        monitor.save_current_scan(current_records)

        logging.info("Route53 Monitor completed successfully")
    except Exception as e:
        logging.error(f"Error in Route53 Monitor: {e}")
        raise

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--loop':
        print("Running in loop mode every 3 seconds...")
        while True:
            main()
            time.sleep(3)
    else:
        main() 