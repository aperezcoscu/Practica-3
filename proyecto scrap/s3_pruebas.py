import boto3

# Crear una sesión de Boto3 y mostrar las credenciales actuales
session = boto3.Session()
credentials = session.get_credentials()
current_credentials = credentials.get_frozen_credentials()

print("Access Key:", current_credentials.access_key)
print("Secret Key:", current_credentials.secret_key)

# Crear un cliente de S3 y probar una operación simple
s3_client = session.client('s3')
response = s3_client.list_buckets()
print("Buckets:", response['Buckets'])
