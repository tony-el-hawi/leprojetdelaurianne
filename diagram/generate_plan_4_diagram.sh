#!/bin/bash
set -e

# Generate Terraform plan JSON
terraform plan -out=plan.tfplan
terraform show -json plan.tfplan > plan.json

# Run the diagram generator
python generate_diagram.py
