import subprocess
import urllib.request
import urllib.error
import socket
import platform
import concurrent.futures
from datetime import datetime

def check_ping(host):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    timeout_param = '-w' if platform.system().lower() == 'windows' else '-W'
    timeout_val = '1500' if platform.system().lower() == 'windows' else '1'
    
    command = ['ping', param, '1', timeout_param, timeout_val, host]

    try:
        # Hide window with CREATE_NO_WINDOW so it's clean on Windows
        creationflags = subprocess.CREATE_NO_WINDOW if platform.system().lower() == 'windows' else 0
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=creationflags)
        return result.returncode == 0
    except Exception:
        return False

def check_web(host, protocol="https", timeout=2):
    url = f"{protocol}://{host}"
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        response = urllib.request.urlopen(req, timeout=timeout)
        return response.getcode() < 400
    except Exception:
        return False

def check_host(ip, host):
    ping_ok = check_ping(host)
    http_ok = check_web(host, protocol="http")
    https_ok = check_web(host, protocol="https")
    return {
        'ip': ip,
        'host': host,
        'ping': ping_ok,
        'http': http_ok,
        'https': https_ok
    }

def log_status(results, filename="network_status.txt"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Using 'w' to overwrite so the user only sees the latest bulk report
    with open(filename, "w", encoding="utf-8") as f:
        header = f"--- Network Status Report: {timestamp} ---\n"
        f.write(header)
        for data in results:
            ping_status = "UP" if data['ping'] else "DOWN"
            http_status = "UP" if data['http'] else "DOWN"
            https_status = "UP" if data['https'] else "DOWN"
            
            log_line = f"IP: {data['ip']:<15} | Host: {data['host']:<30} | Ping: {ping_status:<4} | HTTP: {http_status:<4} | HTTPS: {https_status:<4}\n"
            f.write(log_line)

def main():
    hosts_data = [
        ("10.4.4.160", "jivesso.osisoft.com"),
        ("10.4.4.161", "ssoadfsbe.osisoft.com"),
        ("10.4.4.162", "ssotest.osisoft.com"),
        ("10.4.4.163", "login.osisoft.com"),
        ("10.4.4.164", "dfwebapp.osisoft.com"),
        ("10.4.4.165", "picspreview.osisoft.com"),
        ("10.4.4.166", "myaccount.osisoft.com"),
        ("10.4.4.167", "tslite.osisoft.com"),
        ("10.4.4.168", "chronos.osisoft.int"),
        ("10.4.4.169", "mailr.osisoft.int"),
        ("10.4.4.170", "wwwtest.osisoft.com"),
        ("10.4.4.172", "testmyaccount.osisoft.com"),
        ("10.4.4.173", "licenseviewer.osisoft.int"),
        ("10.4.4.174", "community.osisoft.com"),
        ("10.4.4.174", "signin.osisoft.com"),
        ("10.4.4.174", "support.osisoft.com"),
        ("10.4.4.174", "vcampus.osisoft.com"),
        ("10.4.4.174", "ringcentral.osisoft.com"),
        ("10.4.4.174", "incontact.osisoft.com"),
        ("10.4.4.174", "mimeo.osisoft.com"),
        ("10.4.4.174", "myworkday.osisoft.com"),
        ("10.4.4.174", "explore.osisoft.com"),
        ("10.4.4.174", "testwww.osisoft.com"),
        ("10.4.4.174", "training.osisoft.com"),
        ("10.4.4.174", "quarantine.osisoft.com"),
        ("10.4.4.174", "fmi.osisoft.com"),
        ("10.4.4.174", "concurtest.osisoft.com"),
        ("10.4.4.174", "concur.osisoft.com"),
        ("10.4.4.174", "springcm.osisoft.com"),
        ("10.4.4.174", "search.osisoft.com"),
        ("10.4.4.174", "duoadmin.osisoft.com"),
        ("10.4.4.174", "pluralsight.osisoft.com"),
        ("10.4.4.174", "survey.learning.osisoft.com"),
        ("10.4.4.174", "boomi.osisoft.com"),
        ("10.4.4.175", "osiroleservice.osisoft.com"),
        ("10.4.4.176", "webmail.osisoft.com"),
        ("10.4.4.176", "ars.aveva.com"),
        ("10.4.4.177", "my.osisoft.com"),
        ("10.4.4.178", "sso-admin.osisoft.com"),
        ("10.4.4.179", "sso-admintest.osisoft.com"),
        ("10.4.4.180", "ssoprofiler.osisoft.ext"),
        ("10.4.4.181", "sso-userstore.osisoft.ext")
    ]
    
    results = []
    
    # Use ThreadPoolExecutor to run tests concurrently for significantly faster speeds
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        future_to_host = {executor.submit(check_host, ip, host): (ip, host) for ip, host in hosts_data}
        
        # Gather responses into a dictionary as they complete
        completed_data = {}
        for future in concurrent.futures.as_completed(future_to_host):
            try:
                data = future.result()
                completed_data[data['host']] = data
            except Exception:
                pass
                
        # Maintain original order
        for ip, host in hosts_data:
            if host in completed_data:
                results.append(completed_data[host])
                
    log_status(results, "network_status.txt")
    print("Report generated successfully directly targeting both HTTP and HTTPS checks.")

if __name__ == "__main__":
    main()
