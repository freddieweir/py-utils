# 1Password Fastmail Alias Script

The `1P_fastmail_alias.py` script allows you to create a Fastmail masked email alias and store it in 1Password.

## Setup

1. Copy `.env.template` to `.env`:
   ```bash
   cp .env.template .env
   ```

2. Edit the `.env` file and add your Fastmail API token:
   ```
   FASTMAIL_TOKEN=your_fastmail_api_token_here
   ```

3. (Optional) Add a default 1Password vault and default tags:
   ```
   DEFAULT_VAULT=Personal
   DEFAULT_TAGS=email,generated
   ```

## Requirements

- 1Password CLI installed and authenticated (`op signin`)
- Fastmail account with API access
- Python 3.6+

## Usage

```bash
python 1P_fastmail_alias.py --title "Example Service" --domain "example.com" --description "My Example Account"
```

### Testing with Dry Run

You can use the `--dry-run` flag to simulate the process without actually creating anything:

```bash
python 1P_fastmail_alias.py --title "Example Service" --domain "example.com" --dry-run
```

This will show you what would happen - including the masked email that would be created and the 1Password item details - without making any actual API calls or changes.

## Examples

Here are some practical examples to help you get started:

### Basic Example (Using .env for credentials)

```bash
# Create a masked email for Amazon with default settings
python 1P_fastmail_alias.py --title "Amazon" --domain "amazon.com" --description "Shopping account"
```

### Specifying a Vault

```bash
# Store the login in a specific vault
python 1P_fastmail_alias.py --title "Netflix" --domain "netflix.com" --vault "Entertainment"
```

### Adding Tags and URL

```bash
# Add tags and a URL
python 1P_fastmail_alias.py --title "GitHub" --domain "github.com" --tags dev programming --url "https://github.com"
```

### Custom Email Prefix

```bash
# Specify a custom prefix for the email
python 1P_fastmail_alias.py --title "Twitter" --domain "twitter.com" --prefix "tw"
```

### Adding Notes

```bash
# Add notes to the login item
python 1P_fastmail_alias.py --title "Bank Account" --domain "mybank.com" --notes "Personal checking account"
```

### Using Command Line for API Tokens

```bash
# Provide Fastmail token via command line
python 1P_fastmail_alias.py --title "Reddit" --domain "reddit.com" --fastmail-token "your-token-here"
```

### Complete Example

```bash
# Combine multiple parameters
python 1P_fastmail_alias.py \
  --title "Work Email" \
  --domain "company.com" \
  --description "Company email alias" \
  --vault "Work" \
  --tags work email important \
  --url "https://company.com/mail" \
  --notes "Use for work-related subscriptions only" \
  --prefix "work"
```

### Testing with Dry Run

```bash
# Test the same command without creating anything
python 1P_fastmail_alias.py \
  --title "Work Email" \
  --domain "company.com" \
  --description "Company email alias" \
  --vault "Work" \
  --tags work email important \
  --dry-run
```

## Parameters

- `--title` (required): Title for the 1Password item
- `--vault`: 1Password vault to store the item in (can be set in .env)
- `--domain`: Domain for the masked email (e.g., example.com)
- `--description`: Description for the masked email
- `--prefix`: Prefix for the masked email
- `--tags`: Tags for the 1Password item (adds to default tags)
- `--url`: URL for the 1Password item
- `--notes`: Notes for the 1Password item
- `--fastmail-token`: Fastmail API token (can be set in .env)
- `--fastmail-account`: Fastmail account ID (can be set in .env)
- `--dry-run`: Simulate the process without creating anything 