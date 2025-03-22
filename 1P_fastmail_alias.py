#!/usr/bin/env python3
import os
import json
import argparse
import subprocess
import requests
import secrets
import string
import sys
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

# Import our module_venv helper
from module_venv import AutoVirtualEnvironment

# Setup virtual environment with required packages
auto_venv = AutoVirtualEnvironment(auto_packages=['requests', 'python-dotenv'])
auto_venv.auto_switch()

# Import dotenv after we're in the virtual environment
try:
    from dotenv import load_dotenv
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
    from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class OnePasswordClient:
    """Client for interacting with 1Password CLI"""
    
    def __init__(self, dry_run=False):
        """Initialize the 1Password client"""
        # Verify op CLI is installed
        self._check_op_installed()
        self.dry_run = dry_run
    
    def _check_op_installed(self):
        """Check if the 1Password CLI is installed"""
        try:
            subprocess.run(['op', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("1Password CLI (op) not found. Please install it from https://1password.com/downloads/command-line/")
    
    def is_signed_in(self) -> bool:
        """Check if the user is signed in to 1Password"""
        try:
            subprocess.run(['op', 'account', 'list'], capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def create_login_item(self, title: str, vault: str, username: str, password: Optional[str] = None, 
                         url: Optional[str] = None, notes: Optional[str] = None, tags: Optional[list] = None) -> Dict[str, Any]:
        """Create a new login item in 1Password"""
        
        # Base command and arguments
        cmd = ['op', 'item', 'create', '--category', 'login', '--title', title, '--vault', vault]
        
        # Add optional fields
        if username:
            cmd.extend(['username', username])
        
        if password:
            cmd.extend(['password', password])
        elif password is None:  # Generate password only if None (not empty string)
            cmd.extend(['--generate-password'])
            
        if url:
            cmd.extend(['--url', url])
            
        if notes:
            cmd.extend(['--notes', notes])
            
        if tags:
            for tag in tags:
                cmd.extend(['--tags', tag])
        
        # If dry run, just print the command (with password masked) and return a mock response
        if self.dry_run:
            # Create a safe copy of the command for printing (mask the password)
            safe_cmd = cmd.copy()
            if password:
                password_index = safe_cmd.index('password') + 1
                safe_cmd[password_index] = '********'
            
            print("[DRY RUN] Would execute command: " + " ".join(str(arg) for arg in safe_cmd))
            
            # Return a mock response
            return {
                "id": "dry-run-item-id",
                "title": title,
                "vault": {
                    "id": "dry-run-vault-id",
                    "name": vault
                },
                "category": "LOGIN",
                "urls": [{"primary": True, "href": url}] if url else [],
                "fields": [
                    {"id": "username", "type": "STRING", "purpose": "USERNAME", "label": "username", "value": username},
                    {"id": "password", "type": "CONCEALED", "purpose": "PASSWORD", "label": "password", "value": "********"}
                ]
            }
            
        # Otherwise, run the command
        try:
            result = subprocess.run(cmd, capture_output=True, check=True, text=True)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to create item in 1Password: {e.stderr}")

class FastmailClient:
    """Client for interacting with Fastmail API to create masked emails"""
    
    def __init__(self, api_token: str, account_id: Optional[str] = None, dry_run=False):
        """Initialize the Fastmail client"""
        self.api_token = api_token
        self.account_id = account_id
        self.app_name = "py-1p-fastmail-alias"
        self.session_endpoint = "https://api.fastmail.com/jmap/session"
        self.dry_run = dry_run
        
        if not self.dry_run:
            self.session_data = self._get_session()
            
            # If account_id is not provided, use the primary account
            if not self.account_id:
                self.account_id = self._get_primary_account_id()
        else:
            # For dry run, use mock session data
            self.session_data = {"apiUrl": "https://api.fastmail.com/jmap/api"}
            if not self.account_id:
                self.account_id = "dry-run-account-id"
    
    def _get_session(self) -> Dict[str, Any]:
        """Get session information from Fastmail API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }
        
        response = requests.get(self.session_endpoint, headers=headers)
        
        if response.status_code != 200:
            raise RuntimeError(f"Failed to get session: {response.status_code} {response.text}")
            
        return response.json()
    
    def _get_primary_account_id(self) -> str:
        """Get the primary account ID for masked email"""
        masked_email_capability = "https://www.fastmail.com/dev/maskedemail"
        
        if masked_email_capability not in self.session_data.get("primaryAccounts", {}):
            raise RuntimeError("No primary account found for masked email capability")
            
        return self.session_data["primaryAccounts"][masked_email_capability]
    
    def _get_api_endpoint(self) -> str:
        """Get the API endpoint from session data"""
        return self.session_data.get("apiUrl", "https://api.fastmail.com/jmap/api")
    
    def create_masked_email(self, domain: Optional[str] = None, 
                           description: Optional[str] = None,
                           prefix: Optional[str] = None) -> Dict[str, Any]:
        """Create a new masked email address"""
        
        # If dry run, just print the request and return a mock response
        if self.dry_run:
            print("[DRY RUN] Would create masked email with:")
            print(f"  Account ID: {self.account_id}")
            print(f"  Domain: {domain or 'any'}")
            print(f"  Description: {description or 'none'}")
            print(f"  Prefix: {prefix or 'none'}")
            
            # Generate a mock email address
            mock_prefix = prefix or f"mock{secrets.token_hex(4)}"
            mock_domain = domain or "fastmail.com"
            mock_email = f"{mock_prefix}@{mock_domain}"
            
            # Return a mock response
            return {
                "id": "dry-run-email-id",
                "email": mock_email,
                "forDomain": domain or "",
                "description": description or "",
                "state": "enabled",
                "createTime": "2023-01-01T00:00:00Z"
            }
        
        # Set up the API request
        request_data = {
            "using": [
                "urn:ietf:params:jmap:core",
                "https://www.fastmail.com/dev/maskedemail"
            ],
            "methodCalls": [
                [
                    "MaskedEmail/set",
                    {
                        "accountId": self.account_id,
                        "create": {
                            "new": {
                                "state": "enabled",
                                "forDomain": domain or "",
                                "description": description or "",
                                "emailPrefix": prefix or "",
                                "createdBy": self.app_name
                            }
                        }
                    },
                    "0"
                ]
            ]
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }
        
        response = requests.post(self._get_api_endpoint(), json=request_data, headers=headers)
        
        if response.status_code != 200:
            raise RuntimeError(f"Failed to create masked email: {response.status_code} {response.text}")
            
        response_data = response.json()
        
        # Parse the response to extract the new masked email
        method_response = response_data.get("methodResponses", [])[0]
        
        if method_response[0] != "MaskedEmail/set":
            raise RuntimeError(f"Unexpected response from Fastmail API: {response_data}")
            
        created = method_response[1].get("created", {})
        
        if not created or "new" not in created:
            raise RuntimeError(f"Failed to create masked email: {response_data}")
            
        return created["new"]

def generate_password(length: int = 24) -> str:
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def get_default_tags() -> list:
    """Get default tags from environment variable"""
    default_tags_str = os.getenv("DEFAULT_TAGS", "")
    if not default_tags_str:
        return []
    return [tag.strip() for tag in default_tags_str.split(",") if tag.strip()]

def main():
    """Main function to create a masked email and store it in 1Password"""
    
    # Check if .env file exists, if not, create from template
    env_file = Path(".env")
    env_template = Path(".env.template")
    
    if not env_file.exists() and env_template.exists():
        print(".env file not found. Please copy .env.template to .env and fill in your credentials.")
        print("cp .env.template .env")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Create a Fastmail masked email and store it in 1Password')
    parser.add_argument('--vault', help='1Password vault to store the item in (default: from .env)')
    parser.add_argument('--title', required=True, help='Title for the 1Password item')
    parser.add_argument('--domain', help='Domain for the masked email (e.g., example.com)')
    parser.add_argument('--description', help='Description for the masked email')
    parser.add_argument('--prefix', help='Prefix for the masked email')
    parser.add_argument('--tags', nargs='+', help='Tags for the 1Password item')
    parser.add_argument('--url', help='URL for the 1Password item')
    parser.add_argument('--notes', help='Notes for the 1Password item')
    parser.add_argument('--fastmail-token', help='Fastmail API token')
    parser.add_argument('--fastmail-account', help='Fastmail account ID')
    parser.add_argument('--dry-run', action='store_true', help='Simulate the process without creating anything')
    
    args = parser.parse_args()
    
    # Get Fastmail API token from environment or argument
    fastmail_token = args.fastmail_token or os.environ.get("FASTMAIL_TOKEN")
    if not fastmail_token and not args.dry_run:
        raise RuntimeError("Fastmail API token not provided. Use --fastmail-token or set FASTMAIL_TOKEN in .env file")
    elif not fastmail_token and args.dry_run:
        fastmail_token = "dry-run-token"
    
    # Get Fastmail account ID from environment or argument
    fastmail_account = args.fastmail_account or os.environ.get("FASTMAIL_ACCOUNT")
    
    # Get default vault from environment if not provided
    vault = args.vault or os.environ.get("DEFAULT_VAULT")
    if not vault and not args.dry_run:
        raise RuntimeError("1Password vault not provided. Use --vault or set DEFAULT_VAULT in .env file")
    elif not vault and args.dry_run:
        vault = "dry-run-vault"
    
    # Merge default tags with provided tags
    default_tags = get_default_tags()
    provided_tags = args.tags or []
    tags = list(set(default_tags + provided_tags))  # remove duplicates
    
    # Create clients with dry run flag
    op_client = OnePasswordClient(dry_run=args.dry_run)
    fastmail_client = FastmailClient(fastmail_token, fastmail_account, dry_run=args.dry_run)
    
    # Check if signed in to 1Password
    if not op_client.is_signed_in() and not args.dry_run:
        raise RuntimeError("Not signed in to 1Password. Please run 'op signin' first")
    
    # Dry run header
    if args.dry_run:
        print("\n===== DRY RUN MODE - NO CHANGES WILL BE MADE =====\n")
    
    # Create masked email
    print(f"{'[DRY RUN] Would create' if args.dry_run else 'Creating'} masked email for domain: {args.domain or 'any'}, description: {args.description or 'none'}")
    masked_email = fastmail_client.create_masked_email(
        domain=args.domain,
        description=args.description,
        prefix=args.prefix
    )
    
    email_address = masked_email.get("email")
    if not email_address:
        raise RuntimeError("Failed to get email address from masked email response")
    
    print(f"{'[DRY RUN] Would create' if args.dry_run else 'Created'} masked email: {email_address}")
    
    # Generate a secure password
    password = generate_password()
    if args.dry_run:
        print(f"[DRY RUN] Would generate password: {'*' * len(password)}")
    
    # Create notes with masked email details
    notes = args.notes or ""
    notes += f"\nMasked Email Details:\n"
    notes += f"Email: {email_address}\n"
    notes += f"For domain: {masked_email.get('forDomain') or 'Any'}\n"
    notes += f"Description: {masked_email.get('description') or 'None'}\n"
    notes += f"Created: {masked_email.get('createTime') or 'Unknown'}\n"
    
    # Create 1Password item
    print(f"{'[DRY RUN] Would create' if args.dry_run else 'Creating'} 1Password item '{args.title}' in vault '{vault}'")
    item = op_client.create_login_item(
        title=args.title,
        vault=vault,
        username=email_address,
        password=password,
        url=args.url,
        notes=notes,
        tags=tags
    )
    
    # Final output
    if args.dry_run:
        print("\n===== DRY RUN SUMMARY =====")
        print(f"Would create masked email: {email_address}")
        print(f"Would create 1Password item: {args.title} in vault {vault}")
        print(f"Item ID would be: {item.get('id')}")
        print("\nNo changes were made.")
    else:
        print(f"Successfully created 1Password item with masked email")
        print(f"Email: {email_address}")
        print(f"Item ID: {item.get('id')}")
    
if __name__ == "__main__":
    main()
