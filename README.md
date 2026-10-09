# ChatIA

ChatIA es una aplicación web desarrollada con Django que permite a usuarios autenticados mantener conversaciones con una inteligencia artificial mediante un modelo LLM externo integrado a través de la API de NVIDIA.

La aplicación permite crear conversaciones, enviar mensajes, recibir respuestas generadas por IA y conservar el historial completo de cada chat en la base de datos.

Además, cada usuario dispone de su propio perfil y configuración, pudiendo personalizar tanto el comportamiento del modelo como distintos aspectos visuales de la aplicación.

---

## Tecnologías utilizadas

- Python
- Django
- HTMX
- Bootstrap
- HTML / CSS
- SQLite
- Django ORM
- NVIDIA API
- JSON

---

## Usuarios de prueba

Para probar la aplicación se pueden utilizar las siguientes cuentas de usuario:

### Usuario 1

- **Usuario:** `alex`
- **Contraseña:** `Arboleda.2736`

### Usuario 2

- **Usuario:** `gemma`
- **Contraseña:** `Ventanal.0926`

Ambas son cuentas de usuario normales y no disponen de permisos de administración.

---

# Funcionamiento de la aplicación

ChatIA permite que cada usuario disponga de sus propias conversaciones independientes.

Cada conversación pertenece exclusivamente al usuario que la ha creado, por lo que un usuario no puede acceder a las conversaciones de otros usuarios.

## Gestión de conversaciones

La gestión de las sesiones de conversación se ha implementado mediante el modelo `Conversation`.

Desde la página de conversaciones, el usuario puede:

- Crear nuevas conversaciones.
- Consultar conversaciones anteriores.
- Entrar en una conversación y recuperar todo su historial.
- Renombrar conversaciones.
- Eliminar conversaciones propias.

Cada conversación está asociada al usuario autenticado que la creó.

---

## Gestión de mensajes

Los mensajes se almacenan mediante el modelo `Message`.

Cada mensaje está asociado a una conversación y puede pertenecer a:

- El usuario.
- La inteligencia artificial.

De esta forma, la aplicación conserva el historial completo de cada conversación y puede recuperarlo cuando el usuario vuelve a acceder a ella.

---

## Perfil y configuración del usuario

Cada usuario dispone de un perfil propio mediante el modelo `UserProfile`.

En este perfil se almacenan diferentes datos y preferencias:

- Alias.
- Modelo preferido.
- Temperatura del modelo.
- Preferencias visuales del chat.

Desde la página de configuración, cada usuario puede modificar estos valores de forma independiente.

---

## Integración con inteligencia artificial

La integración con la inteligencia artificial se realiza mediante una API externa de **NVIDIA Build**.

Cuando un usuario envía un mensaje:

1. El mensaje es recibido por Django.
2. Se almacena en la conversación correspondiente.
3. La aplicación realiza una petición al modelo LLM mediante la API de NVIDIA.
4. Se utiliza la temperatura configurada por el usuario como parámetro de la petición.
5. Se recibe la respuesta generada por el modelo.
6. La respuesta se procesa y se almacena como un nuevo mensaje.
7. El contenido actualizado de la conversación se muestra al usuario.

Antes de almacenar la respuesta generada por la IA se realiza una limpieza básica de algunos símbolos Markdown para mejorar su representación dentro del chat, manteniendo los saltos de línea.

---

## Uso de HTMX

HTMX se utiliza durante el envío de mensajes para actualizar la conversación de forma dinámica.

Esto permite actualizar únicamente la parte necesaria de la interfaz sin recargar completamente la página después de cada mensaje.

El proceso general es:

1. El usuario envía un mensaje.
2. HTMX realiza la petición al backend.
3. Django procesa el mensaje y consulta el modelo de IA.
4. Se guardan los nuevos mensajes.
5. Django devuelve el fragmento HTML actualizado.
6. HTMX sustituye únicamente la parte correspondiente del chat.

---

# Recursos implementados

La aplicación expone los siguientes recursos:

| Recurso | Métodos | Descripción |
|---|---|---|
| `/` | `GET` | Página principal pública de la aplicación |
| `/accounts/login/` | `GET`, `POST` | Formulario e inicio de sesión |
| `/accounts/logout/` | `POST` | Cierre de sesión del usuario autenticado |
| `/conversations/` | `GET` | Lista las conversaciones del usuario autenticado |
| `/conversations/new/` | `POST` | Crea una nueva conversación |
| `/conversations/<id>/` | `GET` | Muestra una conversación concreta junto con sus mensajes |
| `/conversations/<id>/send/` | `POST` | Envía un mensaje y actualiza el chat mediante HTMX |
| `/conversations/<id>/delete/` | `POST` | Elimina una conversación perteneciente al usuario |
| `/conversations/<id>/rename/` | `POST` | Modifica el título de una conversación |
| `/conversations/<id>/json/` | `GET` | Devuelve una conversación completa y sus mensajes en formato JSON |
| `/profile/` | `GET` | Muestra el perfil, configuración y estadísticas del usuario |
| `/settings/` | `GET`, `POST` | Muestra y permite modificar la configuración del usuario |
| `/help/` | `GET` | Página de ayuda de la aplicación |
| `/admin/` | `GET`, `POST` | Panel de administración proporcionado por Django |

---

# Configuración de la API de NVIDIA

Para utilizar las funcionalidades de inteligencia artificial es necesario disponer de una **API Key de NVIDIA**.

La clave no se incluye en el repositorio por motivos de seguridad.

La aplicación obtiene esta información desde un fichero `.env`.

## 1. Obtener una API Key

Es necesario disponer de una API Key válida para acceder al servicio utilizado de NVIDIA Build.

Cada persona que ejecute el proyecto debe utilizar su propia clave.

## 2. Crear el archivo `.env`

Dentro del proyecto se debe crear un archivo llamado:

```text
.env
```

En él se configura la clave utilizada para realizar las peticiones a NVIDIA.

Por ejemplo:

```env
NVIDIA_API_KEY=tu_api_key_de_nvidia
```

Sustituye `tu_api_key_de_nvidia` por tu propia clave.

## 3. Proteger la API Key

El fichero `.env` contiene información sensible y no debe subirse al repositorio.

Debe estar incluido en `.gitignore`:

```gitignore
.env
```

De esta forma cada usuario puede utilizar sus propias credenciales sin almacenarlas públicamente en GitHub.

---

# Puesta en marcha

## 1. Clonar el repositorio

```bash
git clone https://github.com/alejandro-calvo/chatia.git
cd chatia
```

## 2. Crear un entorno virtual

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

## 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

## 4. Configurar la API de NVIDIA

Crea el fichero `.env` e introduce tu propia API Key de NVIDIA siguiendo las instrucciones de la sección anterior.

## 5. Aplicar las migraciones

```bash
python manage.py migrate
```

## 6. Iniciar el servidor

```bash
python manage.py runserver
```

La aplicación estará disponible normalmente en:

```text
http://127.0.0.1:8000/
```

---

# Cómo utilizar ChatIA

Una vez iniciada la aplicación:

1. Accede a la página principal.
2. Inicia sesión con una cuenta de usuario.
3. Accede a la sección de conversaciones.
4. Crea una nueva conversación.
5. Entra en la conversación.
6. Escribe un mensaje.
7. La aplicación enviará el contenido al modelo LLM mediante la API de NVIDIA.
8. La respuesta aparecerá automáticamente en el chat.
9. Tanto el mensaje del usuario como la respuesta de la IA quedarán almacenados.
10. Posteriormente se podrá volver a acceder a la conversación y recuperar todo su historial.

Desde la lista de conversaciones también es posible:

- Crear nuevas conversaciones.
- Recuperar conversaciones anteriores.
- Renombrar una conversación.
- Eliminar una conversación.

Desde la página de configuración se pueden modificar las preferencias individuales del usuario.

---

# Funcionalidades adicionales

## Favicon e imagen de cabecera

Se ha añadido una imagen propia cargada desde la carpeta `static`.

Esta imagen se utiliza tanto como logo en la cabecera de la aplicación como favicon de la pestaña del navegador.

---

## Personalización visual del chat

Cada usuario puede personalizar el aspecto de los mensajes desde la página de configuración.

Es posible modificar:

- Fondo de los mensajes del usuario.
- Fondo de los mensajes de la IA.
- Color de la letra.
- Tipo de letra utilizado en los mensajes.

Estas preferencias se almacenan individualmente para cada usuario.

---

## Renombrado de conversaciones

Las conversaciones pueden cambiar de título desde la lista de chats.

La modificación se realiza mediante una petición `POST` y únicamente afecta a conversaciones pertenecientes al usuario autenticado.

---

## Borrado de conversaciones

Los usuarios pueden eliminar sus propias conversaciones desde la lista de chats.

La operación se realiza mediante una petición `POST` y utiliza protección CSRF de Django.

---

## Limpieza de respuestas de la IA

Antes de guardar las respuestas generadas por el modelo, la aplicación elimina algunos símbolos Markdown para mejorar su visualización en el chat.

Los saltos de línea de las respuestas se mantienen.

---

## Temperatura configurable

Cada usuario puede establecer una temperatura desde su página de configuración.

Este valor no es únicamente visual, sino que se utiliza realmente como parámetro en la llamada a la API del modelo LLM.

Esto permite modificar el comportamiento de las respuestas de forma individual para cada usuario.

---

## Representación JSON de conversaciones

La aplicación dispone de un recurso:

```text
/conversations/<id>/json/
```

que permite recuperar una conversación completa junto con sus mensajes en formato JSON.

---

# Autenticación y seguridad

Todas las páginas de la aplicación, salvo la página principal pública, están protegidas mediante el sistema de autenticación de Django.

Si un usuario no autenticado intenta acceder a un recurso protegido, es redirigido al formulario de inicio de sesión.

Además:

- Cada conversación está asociada a un usuario.
- Cada usuario solo puede consultar y modificar sus propias conversaciones.
- Las operaciones de modificación utilizan peticiones `POST`.
- Las operaciones correspondientes cuentan con protección CSRF.
- La API Key de NVIDIA se almacena mediante un fichero `.env`.
- Las credenciales sensibles no se incluyen en el repositorio público.

---

# Interfaz

La aplicación utiliza **Bootstrap** para la maquetación general y CSS propio para personalizar la interfaz.

Los ficheros estáticos se utilizan para cargar:

- Bootstrap.
- Estilos personalizados.
- Logo.
- Favicon.

---

# Tests

Se han añadido tests extremo a extremo para comprobar los principales recursos y funcionalidades de la aplicación.

Estos tests permiten comprobar el comportamiento de las partes principales del sistema, incluyendo acceso a recursos, autenticación y funcionamiento general de la aplicación.

---

# Contexto del proyecto

ChatIA fue desarrollado como proyecto académico durante el **Grado en Ingeniería Telemática de la Universidad Rey Juan Carlos**.

El objetivo principal fue desarrollar una aplicación web completa utilizando Django e integrar en un mismo proyecto:

- Autenticación de usuarios.
- Persistencia de información.
- Gestión de conversaciones y mensajes.
- Interacción dinámica mediante HTMX.
- Integración con un modelo LLM externo.
- Configuración individual por usuario.
- Representación de información mediante JSON.
- Seguridad y control de acceso.
- Tests de funcionamiento.
