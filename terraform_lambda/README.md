# Deployment AWS with Terraform

## About <a name = "about"></a>

Creates AWS Lambda function with Trigger (which triggers Lambda when .csv file is added to the folder1) and 
CloudWatch event on 18pm MON-FRI. 
This function has following features described in my_methods.py: read, simple filter, write.

## Usage <a name = "usage"></a>

In case to deploy this Lambda function with Terraform you need to download the .zip file, main.tf, lambda_function.py.

Setup bucket name and database instance name in main.tf and lambda_function.py.
Then: add updated lambda_function.py to .zip file (zip -g my-deployment-package.zip lambda_function.py).

After that use terraform init and terraform apply to run the terraform template.
NOTE: use region 'us-west-1'.