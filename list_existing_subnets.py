import boto3

ec2 = boto3.client('ec2', region_name='us-west-2')
vpc_id = 'vpc-04eac69b16fcd8b68'

response = ec2.describe_subnets(
    Filters=[
        {'Name': 'vpc-id', 'Values': [vpc_id]}
    ]
)

print(f"  CIDR: {subnet['CidrBlock']}, AZ: {subnet['AvailabilityZone']}, Subnet ID: {subnet['SubnetId']}")
