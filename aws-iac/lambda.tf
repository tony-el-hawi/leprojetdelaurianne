# Lambda Functions
resource "aws_lambda_function" "manage_items" {
  filename      = "${path.module}/lambda_build/lambda.zip"
  function_name = "${var.project_name}-manage-items"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.handler"
  runtime       = "python3.12"
  
  environment {
    variables = {
      TABLE_NAME    = aws_dynamodb_table.items.name
      ORDERS_TABLE  = aws_dynamodb_table.orders.name
      BUCKET_NAME   = aws_s3_bucket.images.bucket
    }
  }
  
  # This forces Terraform to detect changes in the zip file
  source_code_hash = filebase64sha256("lambda_build/lambda.zip")
}


# Lambda permissions
resource "aws_lambda_permission" "manage_items" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.manage_items.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}
