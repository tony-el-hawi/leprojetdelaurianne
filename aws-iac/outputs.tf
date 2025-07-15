# Outputs
output "api_gateway_url" {
  value = "https://${aws_api_gateway_rest_api.api.id}.execute-api.${var.aws_region}.amazonaws.com/${aws_api_gateway_stage.stage.stage_name}/items"
}

# output "s3_bucket_name" {
#   value = aws_s3_bucket.images.bucket
# }