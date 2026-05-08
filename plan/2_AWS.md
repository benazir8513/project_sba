# AWS Setup Guide — Step by Step

> **You don't have an AWS account yet. This guide takes you from zero to deploying your first Lambda via Terraform, all on the Free Tier.**

> **Prerequisites from [1_plan.md](./1_plan.md):** You should have `mise`, `uv`, and your Python project set up before starting this guide.

---

## Table of Contents

1. [Create Your AWS Account](#1-create-your-aws-account)
2. [Understand the Free Tier](#2-understand-the-free-tier)
3. [Set Up Billing Alerts (Do This FIRST)](#3-set-up-billing-alerts)
4. [Secure Your Account with IAM](#4-secure-your-account-with-iam)
5. [Install and Configure AWS CLI](#5-install-and-configure-aws-cli)
6. [Install Terraform via mise](#6-install-terraform-via-mise)
7. [Set Up the tf Folder Structure](#7-set-up-the-tf-folder-structure)
8. [Write Your First Terraform Config](#8-write-your-first-terraform-config)
9. [Deploy Your First Lambda](#9-deploy-your-first-lambda)
10. [gitignore Updates](#10-gitignore-updates)
11. [Cheat Sheet](#11-cheat-sheet)

---

## 1. Create Your AWS Account

### Steps

1. Go to [https://aws.amazon.com/free/](https://aws.amazon.com/free/) and click **"Create a Free Account"**
2. Use a **dedicated email** (not your work email). Suggestion: `yourname+aws@gmail.com`
3. Choose **Personal** account type
4. You **will need a credit card** — AWS requires one even for Free Tier. You won't be charged if you stay within limits and set up billing alerts
5. Choose the **Basic (Free)** support plan
6. Verify your phone number and complete sign-up

### Important Notes

- The **12-month free tier clock starts immediately** from account creation — not from first usage
- Some services are **always free** (Lambda, DynamoDB up to limits), some are **12-month free** (EC2 t2.micro, S3 5GB), some are **trial only**
- **Never use the root account for daily work** — create an IAM user in Section 4
- Write down your **account ID** (12-digit number)

---

## 2. Understand the Free Tier

### What's Free (What We'll Use)

| Service | Free Tier Limit | Type | Notes |
|---|---|---|---|
| **Lambda** | 1M requests/month + 400,000 GB-seconds | Always Free | More than enough for learning |
| **S3** | 5 GB storage, 20K GET, 2K PUT | 12-Month Free | For Terraform state and Lambda zips |
| **CloudWatch Logs** | 5 GB ingestion/month | Always Free | Lambda logs go here automatically |
| **CloudWatch Alarms** | 10 alarms | Always Free | For billing alerts |
| **IAM** | Unlimited | Always Free | Users, roles, policies — no charge |
| **DynamoDB** | 25 GB + 25 read/write units | Always Free | Managed DB option for later |
| **AWS Budgets** | 2 budgets | Always Free | Cost monitoring |

### What's NOT Free (Avoid These)

| Service | Why It Costs Money |
|---|---|
| **NAT Gateway** | ~$0.045/hour — adds up fast |
| **ECS/Fargate** | Free tier is very limited |
| **RDS** | 12-month free tier only (750 hrs t2.micro) |
| **Elastic IP** | Free only when attached to running instance |
| **Data Transfer** | First 1GB/month free, then $0.09/GB out |

**Rule of Thumb:** If a tutorial tells you to create a VPC, NAT Gateway, or load balancer — stop and check costs first.

---

## 3. Set Up Billing Alerts

> **Do this IMMEDIATELY after creating your account. Before creating any resources.**

### 3a: Enable Billing Alerts

1. Sign in as **root user**
2. Go to **Billing and Cost Management** then **Billing preferences**
3. Enable:
   - Receive AWS Free Tier alerts
   - Enter your email address
4. Save

### 3b: Create a $1 Budget Alarm

1. Go to **AWS Budgets** then **Create a budget**
2. Choose **Customized - Cost budget**
3. Configure:
   - **Name:** `monthly-spending-alarm`
   - **Period:** Monthly
   - **Amount:** `$1.00`
4. Add notification at 100% threshold with your email
5. Create

### 3c: Create a $0 Budget (Extra Safety)

Repeat with `$0.01` budget named `zero-cost-alarm`. Alerts you the moment anything costs money.

---

## 4. Secure Your Account with IAM

### 4a: Secure the Root Account

1. Go to **IAM** then **Security credentials** (as root)
2. Enable **MFA** — choose **Authenticator app** (the TOTP option)
3. **MFA device name:** just a label for your reference — e.g. `root-microsoft-authenticator`
4. Scan the QR code with your authenticator app:
   - **Microsoft Authenticator:** tap **+** → **Other account (Google, Facebook, etc.)** → scan
   - Being signed into Microsoft Authenticator with your work email is fine — it doesn't affect this. The app holds TOTP codes from any service regardless of what email you're logged in with.
   - A new AWS entry will appear alongside your work entries. They're completely independent.
5. Enter **two consecutive 6-digit codes** (wait for the code to refresh between entries — AWS requires two to confirm sync)
6. **Never use root again** for daily work after this step

### 4b: Create an IAM User

The AWS console has a multi-step wizard. Here's the exact current flow:

**Step 1 — Specify user details**
1. **IAM** → **Users** → **Create user**
2. **User name:** `sba-dev`
3. Check **"Provide user access to the AWS Management Console — optional"**
4. Console password: **Autogenerated password** is fine
5. Leave **"Users must create a new password at next sign-in"** checked (you'll be prompted to change it on first login)
6. Click **Next**

**Step 2 — Set permissions**
1. **Permissions options** — choose **"Attach policies directly"** (not "Add to group", not "Copy permissions")
2. **Permissions boundary** — leave as **"Create user without a permissions boundary"** (ignore this section entirely for now)
3. In the policy search box, find and check each of these one at a time:
   - `AWSLambda_FullAccess`
   - `AmazonS3FullAccess`
   - `CloudWatchLogsFullAccess`
   - `IAMFullAccess` (needed for Terraform to create Lambda execution roles)

   > In production you'd use least-privilege. For learning, managed policies are fine. Tighten in Phase 4.

4. Click **Next**

**Step 3 — Review and create**
1. Confirm the user name and 4 attached policies look correct
2. Click **Create user**

**Step 4 — Retrieve password**
1. AWS shows a one-time screen with the **Console sign-in URL**, **username**, and **autogenerated password**
2. **Download the `.csv` or copy everything now** — the password is not shown again
3. The console sign-in URL looks like: `https://123456789012.signin.aws.amazon.com/console`

### 4c: Create Access Keys

1. **IAM** then **Users** then `sba-dev` then **Security credentials** then **Create access key**
2. Choose **Command Line Interface (CLI)**
3. Download the `.csv` or copy both keys:
   - `Access Key ID` (starts with `AKIA...`)
   - `Secret Access Key`
4. **Store securely** — you won't see the secret key again

> Your work uses AWS profiles like `ihu-dev-admin` (see `scripts/init_terraform.sh`). For personal use, the default profile is fine.

---

## 5. Install and Configure AWS CLI

### Install

AWS CLI is already installed on your Mac (your work profiles in `~/.aws/config` depend on it). Skip this step.

If you ever need to verify: `aws --version`

### Configure — Named Profile (Safe with Existing Work Setup)

Your work accounts (`ihu-infra-admin`, `ihu-live-admin`, etc.) are all **named SSO profiles** — there is no `[default]` profile and no `~/.aws/credentials` file. Adding your personal account as a named profile is completely safe and won't touch any work config.

```bash
aws configure --profile sba-personal
```

Enter when prompted:
```
AWS Access Key ID:     <your-access-key-id>
AWS Secret Access Key: <your-secret-access-key>
Default region name:   us-east-1
Default output format: json
```

This adds a new `[profile sba-personal]` block to `~/.aws/config` and creates a new `~/.aws/credentials` file. Your `ihu-*` profiles are untouched.

> **Why `us-east-1`?** Most services, best Free Tier support, cheapest pricing, default for billing/IAM.

### Verify

```bash
aws sts get-caller-identity --profile sba-personal
```

Expected:
```json
{
    "UserId": "AIDAEXAMPLEID",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/sba-dev"
}
```

### How to Use the Profile

`AWS_PROFILE` is automatically set to `sba-personal` whenever you `cd` into this project — handled by `direnv` and the `.envrc` file in the project root (already set up). No manual export needed.

You'll see this message when you enter the project directory:
```
direnv: export +AWS_PROFILE
```

And when you leave, it's automatically unset — your work profiles are untouched.

To pass it per-command explicitly (optional, for one-off use outside the project):
```bash
aws lambda list-functions --profile sba-personal
```


---

## 6. Install Terraform via mise

Update `.mise.toml`:

```toml
[tools]
python = "3.14"
terraform = "1.12"
```

Then:

```bash
mise install
terraform --version
```

> `terraform` is now managed by `mise` — no `brew install` needed. The `tf/` folder is already excluded from ruff and pyrefly in `pyproject.toml`.

### Tell Terraform Which AWS Profile to Use

Terraform reads the `AWS_PROFILE` environment variable. This is already handled automatically — `direnv` loads `AWS_PROFILE=sba-personal` from the `.envrc` file in the project root whenever you're inside this project directory. No extra steps needed.

> If you ever `cd` into a `tf/` subfolder, direnv still picks up the `.envrc` from the parent — it searches up the directory tree.

---

## 7. Set Up the tf Folder Structure

### The Key Decision: Execution Order vs. Independent Modules

**Answer: Each folder is independently deployable.** You `cd` into any folder and run `terraform init/plan/apply` on its own. The numeric prefix suggests a **logical first-time setup order** only.

This matches your work pattern in `scripts/init_terraform.sh`:
```bash
for project in */; do
  cd "${SCRIPT_DIR}/../tf/${project}"
  terraform init ...
done
```

### Why Independent Modules?

- **Blast radius:** Messing up Lambda config won't destroy your state backend
- **Speed:** `terraform plan` is fast on small modules
- **Selective deployment:** Deploy only what changed

### Structure

```
tf/
  README.md
  0_backend/
    provider.tf
    main.tf
    variables.tf
    outputs.tf
  1_lambda/
    provider.tf
    main.tf
    variables.tf
    outputs.tf
```

| File | Purpose |
|---|---|
| `provider.tf` | AWS provider, required providers, backend config |
| `main.tf` | Actual resources |
| `variables.tf` | Input variables with descriptions and defaults |
| `outputs.tf` | Exported values (ARNs, URLs, etc.) |

---

## 8. Write Your First Terraform Config

### tf/0_backend/provider.tf

```hcl
terraform {
  required_version = ">= 1.12"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}
```

### tf/0_backend/variables.tf

```hcl
variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}
```

### tf/0_backend/main.tf

```hcl
# Placeholder — in Phase 4 you'll add S3 bucket for remote state
# and DynamoDB table for state locking.
# For now, all modules use local state (terraform.tfstate files).
```

### tf/0_backend/outputs.tf

```hcl
output "aws_region" {
  description = "AWS region being used"
  value       = var.aws_region
}
```

### Test It

```bash
cd tf/0_backend
terraform init
terraform plan
# Should show: No changes. Your infrastructure matches the configuration.
```

---

## 9. Deploy Your First Lambda

### 9a: Create the Handler

```python
# src/handlers/hello.py
def handler(event, context):
    name = event.get("name", "World")
    message = f"Hello, {name}! Deployed with Terraform."
    print(f"Received event: {event}")
    return {"statusCode": 200, "body": message}
```

### 9b: Terraform Config

#### tf/1_lambda/provider.tf

```hcl
terraform {
  required_version = ">= 1.12"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}
```

#### tf/1_lambda/variables.tf

```hcl
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "project-sba"
}
```

#### tf/1_lambda/main.tf

```hcl
# --- IAM Role ---
resource "aws_iam_role" "lambda_exec" {
  name = "${var.project_name}-lambda-exec"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# --- Lambda Function ---
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/../../src/handlers/hello.py"
  output_path = "${path.module}/builds/hello.zip"
}

resource "aws_lambda_function" "hello" {
  function_name    = "${var.project_name}-hello"
  role             = aws_iam_role.lambda_exec.arn
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = "python3.13"
  handler          = "hello.handler"
  memory_size      = 128
  timeout          = 10

  environment {
    variables = { ENVIRONMENT = "dev" }
  }

  tags = {
    Project     = var.project_name
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}

# --- CloudWatch Log Group ---
resource "aws_cloudwatch_log_group" "hello_lambda" {
  name              = "/aws/lambda/${aws_lambda_function.hello.function_name}"
  retention_in_days = 7
  tags = {
    Project   = var.project_name
    ManagedBy = "terraform"
  }
}
```

#### tf/1_lambda/outputs.tf

```hcl
output "lambda_function_name" {
  value = aws_lambda_function.hello.function_name
}

output "lambda_function_arn" {
  value = aws_lambda_function.hello.arn
}

output "lambda_log_group" {
  value = aws_cloudwatch_log_group.hello_lambda.name
}
```

### 9c: Deploy

```bash
cd tf/1_lambda
terraform init
terraform plan       # Review what will be created
terraform apply      # Type 'yes'
```

### 9d: Invoke

```bash
aws lambda invoke \
  --function-name project-sba-hello \
  --payload '{"name": "SBA"}' \
  --cli-binary-format raw-in-base64-out \
  output.json

cat output.json
```

### 9e: Check Logs

```bash
aws logs tail /aws/lambda/project-sba-hello --follow
```

### 9f: Clean Up

```bash
cd tf/1_lambda
terraform destroy    # Type 'yes'
```

> Always `terraform destroy` when done experimenting.

---

## 10. gitignore Updates

Already done. The `.gitignore` in this project includes:

```gitignore
# direnv — local env vars (may contain secrets)
.envrc

# Terraform
**/.terraform/
*.tfstate
*.tfstate.backup
*.tfplan
tf/**/builds/
# Keep .terraform.lock.hcl committed — it pins provider versions (like uv.lock)

# AWS
*.pem
*.key
```

---

## 11. Cheat Sheet

### Terraform

```bash
terraform init       # Download providers, set up backend
terraform plan       # Preview changes (always do this first)
terraform apply      # Create/update resources
terraform destroy    # Delete all resources
terraform fmt        # Format .tf files
terraform validate   # Check syntax without calling AWS
```

### AWS CLI

```bash
aws sts get-caller-identity              # Who am I?
aws lambda list-functions                # List Lambdas
aws lambda invoke --function-name NAME --payload '{}' output.json  # Invoke Lambda
aws logs tail /aws/lambda/NAME --follow  # Stream logs
```

### Cost Safety

```bash
aws lambda list-functions --query 'Functions[].FunctionName'
aws s3 ls
aws ec2 describe-instances --query 'Reservations[].Instances[].InstanceId'
```

---

## What's Next?

Back to [1_plan.md](./1_plan.md):
- **Phase 2:** MongoDB locally + book tracker + deploy handlers via Terraform
- **Phase 3:** Testing, CloudWatch, more handlers
- **Phase 4:** S3 backend for state, trivy scanning, production patterns

