# Usar una imagen base oficial de Python para AWS Lambda
FROM public.ecr.aws/lambda/python:3.8

# Copiar el archivo del script Python y cualquier otro archivo necesario al contenedor
COPY lambda_scrap.py ./
COPY requirements.txt .

# Instalar las dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Establecer el comando para ejecutar tu aplicación
CMD ["lambda_scrap.lambda_handler"]