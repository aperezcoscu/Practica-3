from fastapi import FastAPI, HTTPException
import boto3
from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal
from fastapi import HTTPException
from boto3.exceptions import Boto3Error
from boto3.dynamodb.conditions import Key
import json

app = FastAPI()

# Modelo de Pydantic para estructurar los datos de la respuesta
class VolatilityItem(BaseModel):
    id: str
    Fecha: str
    Fecha_scrap: str
    Strike: float
    Vol_call: Optional[float] = None
    Vol_put: Optional[float] = None



class FutureData(BaseModel):
    Vencimiento: int
    Ant: float

class FuturesList(BaseModel):
    futures: List[FutureData]
    
    

# Convertir a decimal
def convert_decimal(item):
    if isinstance(item, list):
        return [convert_decimal(x) for x in item]
    if isinstance(item, dict):
        return {k: convert_decimal(v) for k, v in item.items()}
    if isinstance(item, Decimal):
        return float(item)
    return item


# Configuración de DynamoDB
def get_dynamodb_table():
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-3')
    return dynamodb.Table('volatiliy_table')



# También puedes agregar otros endpoints si es necesario, por ejemplo para buscar por ID
@app.get("/volatilities/", response_model=List[VolatilityItem])
async def read_volatilities():
    table = get_dynamodb_table()
    try:
        response = table.scan()
        items = response['Items']
        # Convertir Decimals de DynamoDB a float para Pydantic
        for item in items:
            if 'vol_call' in item:
                item['vol_call'] = float(item['vol_call'])
            if 'vol_put' in item:
                item['vol_put'] = float(item['vol_put'])
            if 'strike' in item:
                item['strike'] = float(item['strike'])
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.get("/datos-futuros/", response_model=List[FutureData])
async def read_futures_data():
    s3 = boto3.client('s3', region_name='eu-west-3')
    bucket_name = 'miax-12-scrap-meff'
    key = 'datos_futuros.json'
    
    try:
        response = s3.get_object(Bucket=bucket_name, Key=key)
        data = response['Body'].read().decode('utf-8')
        json_data = json.loads(data)
        return [FutureData(**item) for item in json_data]
    except Boto3Error as e:
        raise HTTPException(status_code=500, detail=f"Error accessing S3: {e}")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")