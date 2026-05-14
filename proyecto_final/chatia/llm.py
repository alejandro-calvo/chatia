import os
# os permite leer variables de entorno como NVIDIA_API_KEY

import json
# json se usa para procesar cada trozo de respuesta que llega en streaming

import requests
# requests permite hacer peticiones HTTP a la API externa

from dotenv import load_dotenv
# load_dotenv carga las variables guardadas en el archivo .env

load_dotenv()
# Cargamos las variables del fichero .env, por ejemplo NVIDIA_API_KEY


def limpiar_respuesta(texto):
    """
    Limpia algunos símbolos de Markdown que la IA puede devolver.

    No cambiamos el contenido de la respuesta, solo quitamos símbolos
    que quedan feos en el chat, como **negrita**, títulos con # o citas con >.
    También cambiamos listas con * por listas con guion normal.
    """

    # Quitamos símbolos típicos de negrita/código en Markdown
    texto = texto.replace("**", "")
    texto = texto.replace("__", "")
    texto = texto.replace("`", "")

    # Procesamos línea por línea para limpiar títulos, citas y listas
    lineas = texto.splitlines()
    lineas_limpias = []

    for linea in lineas:
        linea = linea.strip()

        # Quita citas tipo: > texto
        if linea.startswith(">"):
            linea = linea[1:].strip()

        # Quita títulos tipo: # Título, ## Título, ### Título
        while linea.startswith("#"):
            linea = linea[1:].strip()

        # Cambia listas tipo: * texto por: - texto
        if linea.startswith("* "):
            linea = "- " + linea[2:].strip()

        lineas_limpias.append(linea)

    return "\n".join(lineas_limpias).strip()


def obtener_respuesta_ia(prompt, temperature=0.7):
    """
    Envía el prompt del usuario a NVIDIA Build y devuelve la respuesta del modelo.

    temperature controla si la respuesta será más predecible o más creativa.
    Si no se pasa temperatura, se usa 0.7 como valor por defecto.
    """

    # Leemos la API key desde el archivo .env o desde variable de entorno
    api_key = os.getenv("NVIDIA_API_KEY")

    # Si no hay clave, devolvemos un mensaje de error
    if not api_key:
        return "No se ha encontrado la clave de NVIDIA en el archivo .env."

    # Endpoint de NVIDIA para chat completions
    url = "https://integrate.api.nvidia.com/v1/chat/completions"

    # Cabeceras necesarias para autenticarnos y enviar JSON
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Convertimos la temperatura a float por seguridad
    try:
        temperature = float(temperature)
    except (TypeError, ValueError):
        temperature = 0.7

    # Payload de la petición.
    # Enviamos el prompt del usuario tal cual, sin añadir instrucciones extra.
    payload = {
        "model": "google/gemma-2-2b-it",

        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],

        "temperature": temperature,
        "top_p": 0.7,
        "max_tokens": 1024,
        "stream": True,
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

        # Si hay un error HTTP, se lanza una excepción
        response.raise_for_status()

        # Aquí vamos acumulando el texto que devuelve la IA
        texto_respuesta = ""

        # Recorremos la respuesta en streaming línea por línea
        for line in response.iter_lines():
            if line:
                decoded = line.decode("utf-8")

                # NVIDIA devuelve líneas tipo: data: {...}
                if decoded.startswith("data: "):
                    data = decoded[len("data: "):]

                    # Cuando llega [DONE], termina la respuesta
                    if data == "[DONE]":
                        break

                    try:
                        # Convertimos el fragmento JSON en diccionario
                        chunk = json.loads(data)

                        # Sacamos el contenido generado en este fragmento
                        delta = chunk["choices"][0]["delta"]

                        # Si hay texto, lo añadimos a la respuesta final
                        if "content" in delta:
                            texto_respuesta += delta["content"]

                    except json.JSONDecodeError:
                        # Si algún fragmento no es JSON válido, lo ignoramos
                        continue
                    except (KeyError, IndexError, TypeError):
                        # Si la estructura no viene como esperamos, lo ignoramos
                        continue

        # Si la IA no devuelve contenido útil
        if texto_respuesta.strip() == "":
            return "La IA no devolvió contenido."

        # Limpiamos la respuesta antes de guardarla/mostrarla
        return limpiar_respuesta(texto_respuesta)

    except requests.exceptions.RequestException:
        # Si falla la conexión o la petición HTTP
        return "Error al conectar con NVIDIA Build."