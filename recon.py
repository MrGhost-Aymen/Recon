import os
import subprocess

def run_command(command):
    process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.stdout.decode()

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def main(domain):
    RED = "\033[1;31m"
    RESET = "\033[0m"

    subdomain_path = os.path.join(domain, "subdomains")
    screenshot_path = os.path.join(domain, "screenshots")
    scan_path = os.path.join(domain, "scans")

    # Create directories if they don't exist
    create_directory(domain)
    create_directory(subdomain_path)
    create_directory(screenshot_path)
    create_directory(scan_path)

    print(f"{RED} [+] Launching subfinder ... {RESET}")
    run_command(f"subfinder -d {domain} > {subdomain_path}/found.txt")

    print(f"{RED} [+] Launching assetfinder! .. {RESET}")
    run_command(f"assetfinder {domain} | grep {domain} >> {subdomain_path}/found.txt")

    print(f"{RED} [+] Launching amass {RESET}")
    run_command(f"amass enum -d {domain} >> {subdomain_path}/found.txt")

    print(f"{RED} [+] Finding alive subdomains {RESET}")
    run_command(f"cat {subdomain_path}/found.txt | grep {domain} | sort -u | httprobe -prefer-https | grep https | sed 's/https\\?:\\/\\///' | tee -a {subdomain_path}/alive.txt")

    print(f"{RED} [+] Taking screenshots of alive subdomains ... {RESET}")
    run_command(f"gowitness file -f {subdomain_path}/alive.txt -P {screenshot_path}/ --no-http")

    print(f"{RED} [+] Running nmap on alive subdomains ... {RESET}")
    run_command(f"nmap -iL {subdomain_path}/alive.txt -T4 -p- -A -oN {scan_path}/nmap.txt")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python script.py <domain>")
        sys.exit(1)

    main(sys.argv[1])
