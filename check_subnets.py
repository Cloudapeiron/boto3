import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client('ec2', region_name='us-west-2')

vpc_id = 'vpc-04eac69b16fcd8b68'

# 1. List existing subnets
response = ec2.describe_subnets(
    Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
print("Existing subnets in VPC", vpc_id)

if 'Subnets' in response:
    for subnet in response['Subnets']:
        print(
            f"  CIDR: {subnet['CidrBlock']}, AZ: {subnet['AvailabilityZone']}, Subnet ID: {subnet['SubnetId']}")
        subnet_id = subnet['SubnetId']  # Save one for association later
else:
    print("No subnets found.")
    exit(1)

# 2. Create Security Group
try:
    sg = ec2.create_security_group(
        GroupName='my-security-group',
        Description='Security Group for my VPC',
        VpcId=vpc_id
    )
    ec2.authorize_security_group_ingress(
        GroupId=sg['GroupId'],
        IpPermissions=[
            {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ]
    )
    print(f"Security Group {sg['GroupId']} created and configured.")
except ClientError as e:
    if 'InvalidGroup.Duplicate' in str(e):
        print("Security group already exists.")
    else:
        raise

# 3. Create Route Table
route_table = ec2.create_route_table(VpcId=vpc_id)
route_table_id = route_table['RouteTable']['RouteTableId']
print(f"Created Route Table: {route_table_id}")

# 4. Associate Subnet with Route Table
ec2.associate_route_table(
    RouteTableId=route_table_id,
    SubnetId=subnet_id
)
print(f"Associated Subnet {subnet_id} with Route Table {route_table_id}")

# 5. Create and Attach Internet Gateway
igw_response = ec2.create_internet_gateway()
igw_id = igw_response['InternetGateway']['InternetGatewayId']
print(f"Created Internet Gateway: {igw_id}")

ec2.attach_internet_gateway(
    InternetGatewayId=igw_id,
    VpcId=vpc_id
)
print(f"Attached IGW {igw_id} to VPC {vpc_id}")

# 6. Create Route to IGW
ec2.create_route(
    RouteTableId=route_table_id,
    DestinationCidrBlock='0.0.0.0/0',
    GatewayId=igw_id
)
print("Created route to 0.0.0.0/0 via IGW")
