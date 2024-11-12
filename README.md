# Smart-URL-Checker
# URL Validator and IP Finder Tool

A Python-based tool that validates URLs, retrieves IP addresses, and stores the results efficiently with logging and caching features. The tool can process single URLs or a list of URLs provided in a file. Invalid URLs are saved in a separate file, and IP addresses of valid domains are stored in a JSON file for faster lookups in future executions.

## Features

- **Single or Batch URL Validation**: Validates individual URLs or lists of URLs from a file.
- **Domain Normalization**: Normalizes domains to eliminate duplicate checks for subdomains.
- **IP Address Retrieval and Caching**: Retrieves and caches IP addresses to `domain_ips.json`, saving time on repeated runs.
- **Detailed Logging**: Logs every significant action with timestamps.
- **Results Storage**: Saves invalid URLs to `invalid_urls.txt` and valid URLs with IPs to `valid_urls.json`.

## How It Works

1. **Validation**: The tool validates URLs for correct syntax.
2. **Normalization**: Extracts and normalizes the main domain (e.g., `example.com`).
3. **IP Address Retrieval**:
   - Checks if an IP address for a domain exists in `domain_ips.json`.
   - If the IP is unavailable, it retrieves it, caches it in the JSON file, and logs the result.
4. **Results Storage**:
   - Saves invalid URLs to `invalid_urls.txt`.
   - Saves valid URLs with their corresponding IPs to `valid_urls.json`.

## Requirements

- Python 3.x
- `validators` library for URL validation

Install the required libraries:
```bash
pip install validators
```
Usage

    Clone this repository and navigate to the project folder

Run the tool:

    python main.py

    Follow the prompts:
        Enter 1 to validate a single URL or 2 for a list of URLs.
        For a single URL, type in the URL.
        For a list of URLs, provide the path to the file containing the URLs (one URL per line).

Outputs

    invalid_urls.txt: Contains URLs that failed validation.
    valid_urls.json: Stores valid URLs along with their resolved IPs.
    domain_ips.json: Caches domain-to-IP mappings for faster lookup.
    log_YYYYMMDD_HHMMSS.txt: Detailed log file with timestamps for each step.

Example

Input: A file urls.list with the following:

https://example.com
https://www.example.com
https://invalid-url

Output:

    invalid_urls.txt will contain https://invalid-url.
    valid_urls.json will contain:

    [
        {"url": "https://example.com", "ip": "93.184.216.34"}
    ]

    domain_ips.json caches the IP for example.com for future runs.

License

This project is licensed under the MIT License - see the LICENSE file for details.
Contributing

Pull requests are welcome! For significant changes, please open an issue to discuss them first.

Author: Amir Karimi
GitHub: https://github.com/AmirKarimi1381/
