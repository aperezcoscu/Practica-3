import boto3
from botocore.exceptions import ClientError

def create_dynamodb_table():
    dynamodb = boto3.resource('dynamodb')
    table_name = 'Volatilidades'
    
    try:
        # Intenta crear la tabla
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}  # Clave primaria
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'}  # S significa String
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
        )
        table.wait_until_exists()
        print("Tabla creada exitosamente.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"La tabla {table_name} ya existe.")
        else:
            raise  # Propaga el error si es otro tipo de error
    return dynamodb.Table(table_name)

# Crear la tabla si no existe
tabla = create_dynamodb_table()