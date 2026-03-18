import time
import logging
import datetime
import sys
from netmiko import ConnectHandler

# ==========================================================
# CONFIGURATION
# ==========================================================
# Replace these with your actual Cisco C9300-48P credentials
SWITCH_IP = "192.168.1.1" 
USERNAME = "admin"
PASSWORD = "your_password"
SECRET = "your_enable_secret" # if enable mode is required

CHECK_INTERVAL_MINUTES = 10
# ==========================================================

# Setup logging to keep a record on the local machine
logging.basicConfig(
    filename='cisco_switch_monitor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

cisco_device = {
    'device_type': 'cisco_ios', # Works for CAT9K_IOSXE 17.12.06a
    'host': SWITCH_IP,
    'username': USERNAME,
    'password': PASSWORD,
    'secret': SECRET,
    'global_delay_factor': 2, # Increase delay if the switch is slow to respond
}

def fetch_logs():
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp_str}] Attempting to connect to switch {cisco_device['host']}...")
    
    try:
        # Establish SSH connection
        net_connect = ConnectHandler(**cisco_device)
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Connection successful. Fetching logs...")
        
        # Enter enable mode if needed (uncomment if the user requires enable mode to view logs)
        # net_connect.enable()
        
        # 'show logging' command fetches the buffered logs from the switch
        output = net_connect.send_command("show logging")
        
        # Disconnect gracefully
        net_connect.disconnect()

        # Save the full log output locally
        file_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"switch_logs_{file_timestamp}.txt"
        
        with open(log_filename, 'w') as f:
            f.write(output)
            
        logging.info(f"Successfully fetched logs. Saved to {log_filename}")
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Saved switch output to {log_filename}")

        # Parse output to find ERRORS or WARNINGS
        # Look for Cisco logging syntax, typically "%" followed by severity level
        # E.g., %LINK-3-UPDOWN, %SYS-5-CONFIG_I, %BGP-5-ADJCHANGE
        # Severities 0-3 are usually errors/critical (0=emerg, 1=alert, 2=crit, 3=err)
        errors_found = []
        for line in output.splitlines():
            # Basic parsing to catch common error patterns 
            if "%" in line and ("-0-" in line or "-1-" in line or "-2-" in line or "-3-" in line or "Traceback" in line):
                errors_found.append(line)
                
        if errors_found:
            print("\n*** CRITICAL/ERROR LOGS DETECTED IN THE LAST BUFFER ***")
            logging.warning(f"Found {len(errors_found)} error lines in the recent log output.")
            for err in errors_found:
                print(" -> " + err)
                # You can add email/SMS alert integration here
            print("******************************************************\n")
        else:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] No new critical errors detected.")

    except Exception as e:
        error_msg = f"Failed to connect or fetch logs from {SWITCH_IP}. Error: {str(e)}"
        print(f"\n[ERROR] {error_msg}")
        logging.error(error_msg)

def main():
    print(f"===========================================================")
    print(f"  Cisco C9300-48P Log & Error Monitor")
    print(f"  Target Switch: {SWITCH_IP}")
    print(f"  Interval: Every {CHECK_INTERVAL_MINUTES} minutes")
    print(f"===========================================================\n")
    print("Press Ctrl+C to stop the monitor.\n")
    
    interval_seconds = CHECK_INTERVAL_MINUTES * 60
    
    try:
        while True:
            fetch_logs()
            
            # Wait for the specified interval, showing a countdown is optional
            next_run = datetime.datetime.now() + datetime.timedelta(seconds=interval_seconds)
            print(f"Waiting {CHECK_INTERVAL_MINUTES} minutes. Next run at {next_run.strftime('%H:%M:%S')}...\n")
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\n[INFO] Monitor stopped by user. Exiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()
