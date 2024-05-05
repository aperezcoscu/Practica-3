import boto3


def enviar_correo(resultado):
    client = boto3.client('sns')

    # Asegúrate de que este ARN es correcto y corresponde a un tema existente en SNS
    topic_arn = 'arn:aws:sns:eu-west-3:975050217121:correo_update_volatilidad'

    # Mensaje a enviar
    message = resultado

    # Publica el mensaje en el tema de SNS
    response = client.publish(
        TopicArn=topic_arn,
        Message=message,
        Subject='Prueba de Email SNS'
    )
    return response

# Llamar a la función
enviar_correo()