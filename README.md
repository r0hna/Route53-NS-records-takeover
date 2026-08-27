# Route53 Subdomain Takeover PoC

A proof-of-concept script that simulates a **DNS subdomain takeover** against an Amazon Route 53 hosted zone. It repeatedly creates a hosted zone for a target domain and checks whether AWS assigns name servers that match the target's existing NS records — the condition that makes a takeover possible.

> ⚠️ **Educational / authorized testing only.** This script is a PoC for research and CTF-style labs. Only run it against domains you own or have explicit written permission to test. Unauthorized takeover attempts may violate AWS terms of service and local cybercrime laws.

---

## How It Works

1. The script creates a new Route 53 hosted zone for `TARGET_DOMAIN` with a random caller reference.
2. It reads the name servers AWS assigns to that zone.
3. It compares those name servers against the target's real NS records (`TARGET_NS`).
4. If any name servers **intersect** (match), the takeover condition is met and the script stops — the zone is left alive so records can be added to serve content.

The loop keeps retrying because AWS may assign different name servers on each attempt.

---

## Prerequisites

- Python 3.x
- `boto3` installed:

```bash
pip install boto3
```

- An AWS account with **Route 53** access and valid credentials.

---

## Setup

Set your AWS credentials as environment variables before running:

```bash
export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
export AWS_DEFAULT_REGION="us-east-1"
```

> 🔐 Never commit real credentials. Use IAM roles, environment variables, or the AWS credentials file instead.

---

## Configuration

Edit the two constants at the top of the script:

| Constant | Purpose |
|----------|---------|
| `TARGET_DOMAIN` | The domain you're testing (e.g. `example.com`) |
| `TARGET_NS` | The exact name servers of the target you're trying to match |

## Tool Output
```
(.env) sh-5.3$ python takeover.py 
[*] Starting takeover simulation for example.com...
[*] Target Name Servers: {'ns-1361.awsdns-42.org.', 'ns-775.awsdns-32.net.', 'ns-1855.awsdns-39.co.uk.'}

[-] Attempt 1: No match. Assigned: ['ns-991.awsdns-59.net', 'ns-385.awsdns-48.com']... Deleting zone.
[-] Attempt 2: No match. Assigned: ['ns-854.awsdns-42.net', 'ns-1476.awsdns-56.org']... Deleting zone.
[-] Attempt 3: No match. Assigned: ['ns-1706.awsdns-21.co.uk', 'ns-481.awsdns-60.com']... Deleting zone.
---REDACTED---

[+] SUCCESS on iteration 69!
[+] Hosted Zone ID: /hostedzone/Z086807628NAQWNHZ3VLV
[+] Matched Name Servers: {'ns-1361.awsdns-42.org.'}
[+] The zone has been kept alive. You can now add records to serve content.
```
