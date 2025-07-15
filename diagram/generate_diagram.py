import json
import os
from collections import defaultdict
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Lambda, EC2, ECS, Fargate
from diagrams.aws.database import Dynamodb, RDS, ElastiCache
from diagrams.aws.storage import S3, EBS, EFS
from diagrams.aws.network import APIGateway, CloudFront, ELB, VPC, Route53
from diagrams.aws.mobile import Amplify
from diagrams.aws.management import Cloudwatch
from diagrams.aws.security import IAM, Cognito, WAF
from diagrams.aws.analytics import Kinesis, Athena
from diagrams.aws.integration import SQS, SNS
from diagrams.aws.general import General

# Enhanced resource mapping with more AWS services
RESOURCE_MAP = {
    # Compute
    "aws_lambda_function": Lambda,
    "aws_instance": EC2,
    "aws_ecs_service": ECS,
    "aws_ecs_cluster": ECS,
    "aws_fargate_service": Fargate,
    
    # Database
    "aws_dynamodb_table": Dynamodb,
    "aws_db_instance": RDS,
    "aws_rds_cluster": RDS,
    "aws_elasticache_cluster": ElastiCache,
    
    # Storage
    "aws_s3_bucket": S3,
    "aws_s3_bucket_cors_configuration": S3,
    "aws_s3_bucket_policy": S3,
    "aws_s3_bucket_public_access_block": S3,
    "aws_ebs_volume": EBS,
    "aws_efs_file_system": EFS,
    
    # Network
    "aws_api_gateway_rest_api": APIGateway,
    "aws_api_gateway_v2_api": APIGateway,
    "aws_api_gateway_deployment": APIGateway,
    "aws_api_gateway_integration": APIGateway,
    "aws_api_gateway_integration_response": APIGateway,
    "aws_api_gateway_method": APIGateway,
    "aws_api_gateway_method_response": APIGateway,
    "aws_api_gateway_resource": APIGateway,
    "aws_api_gateway_stage": APIGateway,
    "aws_cloudfront_distribution": CloudFront,
    "aws_lb": ELB,
    "aws_alb": ELB,
    "aws_elb": ELB,
    "aws_vpc": VPC,
    "aws_route53_zone": Route53,
    "aws_route53_record": Route53,
    
    # Mobile/Web
    "aws_amplify_app": Amplify,
    
    # Management
    "aws_cloudwatch_log_group": Cloudwatch,
    "aws_cloudwatch_metric_alarm": Cloudwatch,
    
    # Security
    "aws_iam_role": IAM,
    "aws_iam_policy": IAM,
    "aws_iam_user": IAM,
    "aws_iam_role_policy": IAM,
    "aws_lambda_permission": IAM,
    "aws_cognito_user_pool": Cognito,
    "aws_wafv2_web_acl": WAF,
    
    # Analytics
    "aws_kinesis_stream": Kinesis,
    "aws_athena_database": Athena,
    
    # Integration
    "aws_sqs_queue": SQS,
    "aws_sns_topic": SNS,
    
    # Utilities
    "random_string": General,
}

# Service categories for clustering
SERVICE_CATEGORIES = {
    "Compute": ["aws_lambda_function", "aws_instance", "aws_ecs_service", "aws_ecs_cluster", "aws_fargate_service"],
    "Database": ["aws_dynamodb_table", "aws_db_instance", "aws_rds_cluster", "aws_elasticache_cluster"],
    "Storage": ["aws_s3_bucket", "aws_s3_bucket_cors_configuration", "aws_s3_bucket_policy", "aws_s3_bucket_public_access_block", "aws_ebs_volume", "aws_efs_file_system"],
    "Network & CDN": ["aws_api_gateway_rest_api", "aws_api_gateway_v2_api", "aws_api_gateway_deployment", "aws_api_gateway_integration", "aws_api_gateway_integration_response", "aws_api_gateway_method", "aws_api_gateway_method_response", "aws_api_gateway_resource", "aws_api_gateway_stage", "aws_cloudfront_distribution", "aws_lb", "aws_alb", "aws_elb", "aws_vpc", "aws_route53_zone", "aws_route53_record"],
    "Security & Identity": ["aws_iam_role", "aws_iam_policy", "aws_iam_user", "aws_iam_role_policy", "aws_lambda_permission", "aws_cognito_user_pool", "aws_wafv2_web_acl"],
    "Monitoring & Management": ["aws_cloudwatch_log_group", "aws_cloudwatch_metric_alarm"],
    "Analytics": ["aws_kinesis_stream", "aws_athena_database"],
    "Integration": ["aws_sqs_queue", "aws_sns_topic"],
    "Mobile & Web": ["aws_amplify_app"],
    "Utilities": ["random_string"]
}

def load_resources(json_dir):
    """Load and parse Terraform resources from JSON files"""
    resources = []
    
    if not os.path.exists(json_dir):
        print(f"Directory {json_dir} not found. Please run 'terraform show -json > plan.json' first.")
        return resources
    
    for file in os.listdir(json_dir):
        if file.endswith(".json"):
            file_path = os.path.join(json_dir, file)
            with open(file_path) as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"Error decoding {file}: {e}")
                    continue

                # Handle both terraform plan and state formats
                if "planned_values" in data and "root_module" in data["planned_values"]:
                    # Terraform plan format
                    resources.extend(parse_terraform_plan(data))
                elif "resource" in data:
                    # Terraform configuration format
                    for res_type, res_defs in data["resource"].items():
                        for name, config in res_defs.items():
                            resources.append((res_type, name, config))
                elif "values" in data and "root_module" in data["values"]:
                    # Terraform state format
                    resources.extend(parse_terraform_state(data))
    
    return resources

def parse_terraform_plan(data):
    """Parse resources from terraform plan JSON"""
    resources = []
    root_module = data["planned_values"]["root_module"]
    
    if "resources" in root_module:
        for resource in root_module["resources"]:
            res_type = resource.get("type")
            name = resource.get("name")
            values = resource.get("values", {})
            if res_type and name:
                resources.append((res_type, name, values))
    
    return resources

def parse_terraform_state(data):
    """Parse resources from terraform state JSON"""
    resources = []
    root_module = data["values"]["root_module"]
    
    if "resources" in root_module:
        for resource in root_module["resources"]:
            res_type = resource.get("type")
            name = resource.get("name")
            values = resource.get("values", {})
            if res_type and name:
                resources.append((res_type, name, values))
    
    return resources

def categorize_resources(resources):
    """Group resources by service category"""
    categorized = defaultdict(list)
    uncategorized = []
    
    for res_type, name, config in resources:
        category_found = False
        for category, types in SERVICE_CATEGORIES.items():
            if res_type in types:
                categorized[category].append((res_type, name, config))
                category_found = True
                break
        
        if not category_found and res_type in RESOURCE_MAP:
            uncategorized.append((res_type, name, config))
    
    if uncategorized:
        categorized["Other Services"] = uncategorized
    
    return dict(categorized)

def create_clean_name(name, res_type):
    """Create a clean, readable name for diagram nodes"""
    # Remove common prefixes and make more readable
    clean_name = name.replace("_", " ").title()
    
    # Add service type hint for clarity
    type_hints = {
        "aws_lambda_function": "λ",
        "aws_s3_bucket": "S3",
        "aws_dynamodb_table": "DDB",
        "aws_api_gateway_rest_api": "API",
        "aws_cloudfront_distribution": "CDN"
    }
    
    if res_type in type_hints:
        return f"{type_hints[res_type]} {clean_name}"
    
    return clean_name

def draw_diagram(resources):
    """Generate a clean, organized AWS architecture diagram"""
    if not resources:
        print("No resources found to diagram.")
        return
    
    categorized = categorize_resources(resources)
    
    with Diagram(
        "AWS Infrastructure", 
        show=False, 
        filename="aws_infrastructure", 
        outformat="png",
        graph_attr={
            "fontsize": "16",
            "bgcolor": "white",
            "pad": "1.0",
            "splines": "ortho"
        }
    ):
        all_nodes = {}
        
        # Create clusters for each service category
        for category, category_resources in categorized.items():
            if not category_resources:
                continue
                
            with Cluster(category, graph_attr={"style": "rounded,filled", "fillcolor": "lightgray"}):
                for res_type, name, config in category_resources:
                    if res_type in RESOURCE_MAP:
                        node_class = RESOURCE_MAP[res_type]
                        clean_name = create_clean_name(name, res_type)
                        node = node_class(clean_name)
                        all_nodes[f"{res_type}.{name}"] = node
        
        # Add basic connections based on common patterns
        create_logical_connections(all_nodes, resources)
        
        print(f"\nDiagram generated: aws_infrastructure.png")
        print(f"Total resources: {len(resources)}")
        print(f"Categories: {', '.join(categorized.keys())}")

def create_logical_connections(nodes, resources):
    """Create logical connections between related services"""
    # Common connection patterns
    connections = []
    
    # Find API Gateway -> Lambda connections
    api_gateways = [k for k in nodes.keys() if k.startswith("aws_api_gateway")]
    lambdas = [k for k in nodes.keys() if k.startswith("aws_lambda_function")]
    
    # Connect API Gateway to Lambda (common serverless pattern)
    if api_gateways and lambdas:
        for api in api_gateways[:1]:  # Connect first API Gateway
            for lambda_func in lambdas[:2]:  # to first 2 Lambda functions
                connections.append((nodes[api], nodes[lambda_func]))
    
    # Connect Lambda to DynamoDB (common serverless pattern)
    dynamodb_tables = [k for k in nodes.keys() if k.startswith("aws_dynamodb_table")]
    if lambdas and dynamodb_tables:
        for lambda_func in lambdas[:2]:
            for table in dynamodb_tables[:1]:
                connections.append((nodes[lambda_func], nodes[table]))
    
    # Connect CloudFront to S3 (common static hosting pattern)
    cloudfront = [k for k in nodes.keys() if k.startswith("aws_cloudfront")]
    s3_buckets = [k for k in nodes.keys() if k.startswith("aws_s3_bucket")]
    if cloudfront and s3_buckets:
        connections.append((nodes[cloudfront[0]], nodes[s3_buckets[0]]))
    
    # Apply connections with clean edges
    for source, target in connections:
        source >> Edge(style="dashed", color="gray") >> target

def main():
    """Main function to generate AWS infrastructure diagram"""
    json_dir = "json_out"
    
    print("AWS Infrastructure Diagram Generator")
    print("====================================\n")
    
    # Check for alternative directories if json_out doesn't exist
    if not os.path.exists(json_dir):
        alternatives = [".", "terraform", "tf"]
        for alt_dir in alternatives:
            if os.path.exists(alt_dir) and any(f.endswith(".json") for f in os.listdir(alt_dir)):
                json_dir = alt_dir
                print(f"Using directory: {json_dir}")
                break
        else:
            print(f"No JSON files found. Please ensure you have:")
            print(f"1. Run 'terraform plan -out=plan.tfplan'")
            print(f"2. Run 'terraform show -json plan.tfplan > plan.json'")
            print(f"3. Place the JSON file in the current directory or 'json_out' folder")
            return
    
    resources = load_resources(json_dir)
    
    if not resources:
        print("No Terraform resources found in JSON files.")
        return
    
    print(f"Found {len(resources)} resources")
    
    # Show resource summary
    resource_types = {}
    for res_type, name, config in resources:
        resource_types[res_type] = resource_types.get(res_type, 0) + 1
    
    print("\nResource Summary:")
    for res_type, count in sorted(resource_types.items()):
        status = "✓" if res_type in RESOURCE_MAP else "⚠"
        print(f"  {status} {res_type}: {count}")
    
    unsupported = [rt for rt in resource_types.keys() if rt not in RESOURCE_MAP]
    if unsupported:
        print(f"\n⚠ Unsupported resource types (will be skipped): {', '.join(unsupported)}")
    
    draw_diagram(resources)

if __name__ == "__main__":
    main()
