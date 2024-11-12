import urllib.parse
import validators
import requests
import socket
import logging
import json
from datetime import datetime
import os
import tldextract

# Initialize logging
log_filename = datetime.now().strftime("log_%Y%m%d_%H%M%S.txt")
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Program started.")

# Function to extract root domain (main domain + TLD) without subdomains
def get_root_domain(url):
    extracted = tldextract.extract(url)
    root_domain = f"{extracted.domain}.{extracted.suffix}"
    return root_domain

# Check if URL is valid and reachable
def is_valid_url(url):
    try:
        response = requests.get(url, timeout=3)
        logging.info(f"Checked URL: {url} - Status Code: {response.status_code}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        logging.error(f"RequestException for URL {url}: {e}")
        return False

# Load invalid URLs from file if it exists
def load_invalid_urls():
    if os.path.exists("invalid_urls.txt"):
        with open("invalid_urls.txt", 'r') as file:
            return {line.strip().split(" - ")[0] for line in file}
    return set()

# Save invalid URLs to file
def save_invalid_url(url):
    with open("invalid_urls.txt", 'a') as file:
        file.write(f"{url} - initial_invalid\n")
    logging.info(f"Invalid URL saved to file: {url}")

# Load IP addresses from file if it exists
def load_domain_ips():
    if os.path.exists("domain_ips.json"):
        with open("domain_ips.json", 'r') as file:
            return json.load(file)
    return {}

# Save IP addresses to file
def save_domain_ips(domain_ips):
    with open("domain_ips.json", 'w') as file:
        json.dump(domain_ips, file, indent=4)
    logging.info("Domain IPs saved to domain_ips.json.")

# Get the IP address of the domain
def get_domain_ip(domain, domain_ips):
    root_domain = get_root_domain(domain)
    if root_domain in domain_ips:
        logging.info(f"IP for root domain {root_domain} found in cache: {domain_ips[root_domain]}")
        return domain_ips[root_domain]

    user_input = input(f"Do you have the IP address for {root_domain}? (y/n): ").strip().lower()
    if user_input == 'y':
        ip_address = input("Please enter the IP address: ").strip()
        logging.info(f"User provided IP address for {root_domain}: {ip_address}")
        domain_ips[root_domain] = ip_address
    else:
        try:
            ip_address = socket.gethostbyname(root_domain)
            logging.info(f"Automatically retrieved IP address for {root_domain}: {ip_address}")
            domain_ips[root_domain] = ip_address
        except socket.gaierror:
            logging.error(f"Failed to retrieve IP address for root domain: {root_domain}")
            ip_address = None

    save_domain_ips(domain_ips)
    return ip_address

# Generate alternative URLs based on a valid URL
def generate_alternate_urls(original_url, ip_address=None):
    parsed_url = urllib.parse.urlparse(original_url)
    scheme = parsed_url.scheme
    root_domain = get_root_domain(original_url)
    path = parsed_url.path
    query = parsed_url.query
    fragment = parsed_url.fragment
    alternate_urls = []

    alternate_urls.append(f"{scheme}://{root_domain}{path}?{query}#{fragment}")
    if ip_address:
        alternate_urls.append(f"{scheme}://{ip_address}{path}?{query}#{fragment}")
    if scheme == 'https':
        alternate_urls.append(f"http://{root_domain}{path}?{query}#{fragment}")
    if query:
        encoded_query = urllib.parse.quote(query)
        alternate_urls.append(f"{scheme}://{root_domain}{path}?{encoded_query}#{fragment}")
    if '@' not in parsed_url.netloc:
        alternate_urls.append(f"{scheme}://username:password@{root_domain}{path}?{query}#{fragment}")

    logging.info(f"Generated alternate URLs for {original_url}: {alternate_urls}")
    return alternate_urls

# Process a single URL or list of URLs
def process_urls(urls):
    valid_urls = []
    invalid_urls = load_invalid_urls()  # Load already known invalid URLs to skip

    domain_ips = load_domain_ips()

    # Initial validity check for all URLs
    for url in urls:
        if url in invalid_urls:
            logging.info(f"Skipping known invalid URL: {url}")
            continue

        if is_valid_url(url):
            valid_urls.append(url)
        else:
            save_invalid_url(url)  # Save directly to file
            invalid_urls.add(url)  # Add to in-memory set to skip future checks

    # Process valid URLs
    valid_results = {}
    for url in valid_urls:
        root_domain = get_root_domain(url)
        ip_address = get_domain_ip(root_domain, domain_ips)
        valid_alternates = []
        invalid_alternates = []

        alternate_urls = generate_alternate_urls(url, ip_address)
        for alt_url in alternate_urls:
            if alt_url in invalid_urls:
                logging.info(f"Skipping known invalid alternate URL: {alt_url}")
                continue
            if is_valid_url(alt_url):
                valid_alternates.append(alt_url)
            else:
                invalid_alternates.append(alt_url)
                save_invalid_url(alt_url)
                invalid_urls.add(alt_url)

        valid_results[url] = {
            "original_url": url,
            "valid_alternates": valid_alternates
        }

    with open("valid_urls.json", 'w') as valid_file:
        json.dump(valid_results, valid_file, indent=4)

    logging.info("Results saved successfully.")

# Main function to handle user input and selection
def main():
    print("Select an option:")
    print("1. Check a single URL")
    print("2. Check a list of URLs from a file")
    
    choice = input("Enter 1 or 2: ").strip()
    
    if choice == '1':
        url = input("Please enter the URL to check: ").strip()
        process_urls([url])
    elif choice == '2':
        file_path = input("Please enter the file path of the URL list: ").strip()
        try:
            with open(file_path, 'r') as file:
                urls = {line.strip() for line in file if line.strip()}
            process_urls(urls)
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
            print("The file was not found. Please check the file path.")
    else:
        logging.warning("Invalid choice entered.")
        print("Invalid choice. Please enter '1' or '2'.")

    print("\nResults have been saved to 'valid_urls.json' and 'invalid_urls.txt'")
    logging.info("Program finished. Results saved.")

# Run the main function
main()