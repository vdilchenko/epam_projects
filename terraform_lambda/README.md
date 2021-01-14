# Deployment AWS with Terraform

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Contributing](../CONTRIBUTING.md)

## About <a name = "about"></a>

Creates AWS Lambda function with Trigger (which triggers Lambda when .csv file is added to the folder1) and CloudWatch event on 18pm MON-FRI. This function reads/filters/writes data. 

## Usage <a name = "usage"></a>

In case to deploy this Lambda function with Terraform you need to download the .zip file and main.tf.

Then use terraform init and terraform apply to run the terraform template.
NOTE: use region 'us-west-1'.