output "lambda_function_name" {
  value = aws_lambda_function.project_sba_lambda.function_name
}

output "lambda_function_arn" {
  value = aws_lambda_function.project_sba_lambda.arn
}

output "lambda_log_group" {
  value = aws_cloudwatch_log_group.lambda_log_group.name
}