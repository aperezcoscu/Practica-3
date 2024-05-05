# AWS Application Deployment

Este proyecto está diseñado para mejorar la funcionalidad de una aplicación usando servicios en la nube de AWS, implementando automatizaciones con GitHub Actions y procesando datos de manera eficiente con funciones Lambda.

## Características

- **Plataforma de Hospedaje**: AWS.
- **Automatización con GitHub Actions**:
  - **PR Workflow (`pull_request.yml`)**: Ejecuta flake8 y tests unitarios en cada pull request.
  - **Main Merge Workflow (`merge_main.yml`)**: Despliega la aplicación en AWS en cada merge a la rama main.
  - **Lambda Deployment Workflow (`lambda_deploy.yml`)**: Gestiona el despliegue de funciones Lambda.
- **Funciones AWS Lambda**:
  - **Función de Web Scraping**: Se ejecuta según un cron de AWS EventBridge a las 9:00 AM de lunes a viernes, guarda los datos en el S3 bucket.
  - **Función de Cálculo de Volatilidad**: Procesa los datos del S3 bucket, calcula la volatilidad y los almacena en DynamoDB.
- **AWS EventBridge**: Programa las funciones Lambda con un cron específico.
- **Almacenamiento AWS**:
  - **S3 Bucket (`scrap-miax-12`)**: Almacena los datos extraídos por la función de web scraping.
  - **DynamoDB**: Almacena los resultados de la volatilidad calculados por la función de cálculo.
- **API**:
  - **FastAPI**: Provee una API para que la interfaz de usuario pueda acceder a los datos almacenados en DynamoDB.
- **Interfaz de Usuario (UI)**:
  - **Dash**: Aplicación web que permite visualizar y comparar skews de volatilidad, y muestra la superficie de volatilidad y su evolución.

## Prerequisitos

Para ejecutar este proyecto, necesitarás Python 3.6 o superior, además de las siguientes herramientas:

- AWS CLI configurado con acceso a tu cuenta de AWS.
- Docker (opcional para contenerización local).

