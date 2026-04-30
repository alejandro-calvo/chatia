import os
# os permite leer variables de entorno como NVIDIA_API_KEY

import json
# json se usa para procesar cada trozo de respuesta que llega en streaming

import requests
# requests permite hacer peticiones HTTP a la API externa

from dotenv import load_dotenv
# load_dotenv carga las variables guardadas en el archivo .env

load_dotenv()
# Aquí se cargan automáticamente las variables del .env


def obtener_respuesta_ia(prompt):
    """
    Esta función envía el prompt del usuario a NVIDIA Build
    y devuelve la respuesta generada por el modelo.
    """

    # Leemos la API key desde el archivo .env
    api_key = os.getenv("NVIDIA_API_KEY")

    # Si no existe la clave, devolvemos mensaje de error
    if not api_key:
        return "No se ha encontrado la clave de NVIDIA en el archivo .env."

    # Endpoint de NVIDIA para chat completions
    url = "https://integrate.api.nvidia.com/v1/chat/completions"

    # Cabeceras HTTP necesarias para autenticarse y enviar JSON
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Payload con la información de la petición
    payload = {
        "model": "google/gemma-2-2b-it",
        # Modelo que usamos en la práctica

        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        # Solo enviamos el último prompt del usuario

        "temperature": 0.2,
        # Temperatura baja para respuestas algo más estables

        "top_p": 0.7,
        # Otro parámetro de control de generación

        "max_tokens": 1024,
        # Número máximo de tokens de respuesta

        "stream": True,
        # Pedimos la respuesta en streaming
    }

    try:
        # Enviamos la petición POST a NVIDIA
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            stream=True,
            timeout=60
        )

        # Si la respuesta HTTP tiene error, lanza excepción
        response.raise_for_status()

        # Aquí iremos acumulando el texto que devuelve la IA
        texto_respuesta = ""

        # Recorremos línea por línea la respuesta en streaming
        for line in response.iter_lines():
            if line:
                decoded = line.decode("utf-8")

                # NVIDIA devuelve líneas tipo "data: ..."
                if decoded.startswith("data: "):
                    data = decoded[len("data: "):]

                    # Cuando llega [DONE], se acaba el streaming
                    if data == "[DONE]":
                        break

                    try:
                        # Convertimos ese trozo de texto JSON en diccionario
                        chunk = json.loads(data)

                        # Sacamos la parte nueva de la respuesta
                        delta = chunk["choices"][0]["delta"]

                        # Si hay contenido, lo vamos concatenando
                        if "content" in delta:
                            texto_respuesta += delta["content"]

                    except json.JSONDecodeError:
                        # Si algún trozo no se puede convertir, lo ignoramos
                        continue
                    except (KeyError, IndexError, TypeError):
                        # Si falta alguna clave o viene algo inesperado, lo ignoramos
                        continue

        # Si al final no se ha recibido texto útil
        if texto_respuesta.strip() == "":
            return "La IA no devolvió contenido."

        # Devolvemos la respuesta limpia
        return texto_respuesta.strip()

    except requests.exceptions.RequestException:
        # Si falla la conexión o la petición HTTP
        return "Error al conectar con NVIDIA Build."