# Deployment AWS with Terraform

## About <a name = "about"></a>

Creates AWS Lambda function with Trigger (which triggers Lambda when .csv file is added to the folder1) and 
CloudWatch event on 18pm MON-FRI. 

This function has following features described in my_methods.py: read, simple filter, write.

## Usage <a name = "usage"></a>

In case to deploy this Lambda function with Terraform you need to download the .zip file and main.tf.

Setup following variables in the 'somename'.tfvars file: sg_name, bucket_name, db_instance_name, db_username, db_password, db_name. Each of them is of type string.

After that use terraform init and terraform apply -var-file="somename.tfvars" to run the terraform template with given names and credentials.

NOTE: use region 'us-west-1'.