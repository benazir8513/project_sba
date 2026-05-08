data "aws_iam_policy_document" "lambda_iam_policy_document" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_iam_role" {
  name = "${var.project}-lambda-iam-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_iam_policy_document.json
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
    role       = aws_iam_role.lambda_iam_role.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# --- Lambda Function ---
data "archive_file" "lambda_zip" {
    type        = "zip"
    source_file  = "${path.module}/../../lambda_handler.py"
    output_path = "${path.module}/../../build/lambda_handler.zip"
}

resource "aws_lambda_function" "project_sba_lambda" {
  function_name = "${var.project}-lambda"
  role         = aws_iam_role.lambda_iam_role.arn
  filename = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime = "python${var.python_version}"
  handler = "lambda_handler.handler"
  memory_size = 128
  timeout = 10

  environment {
    variables = {
        ENVIRONMENT = var.environment
    }
  }

  tags = {
    Project = var.project
    Environment = var.environment
    ManagedBy = "terraform"
  }
}

# --- CloudWatch Log Group ---
resource "aws_cloudwatch_log_group" "lambda_log_group" {
    name              = "/aws/lambda/${aws_lambda_function.project_sba_lambda.function_name}"
    retention_in_days = 7
    tags = {
      Project   = var.project
      ManagedBy = "terraform"
    }
}
