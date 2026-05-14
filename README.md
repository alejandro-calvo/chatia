# ENTREGA CONVOCATORIA MAYO

# ENTREGA DE PRÁCTICA

## Datos

* Nombre: Alejandro
* Titulación: Ingeniería Telemática
* Cuenta en laboratorios: PON_AQUI_TU_CUENTA_DE_LABORATORIOS
* Cuenta URJC: PON_AQUI_TU_CUENTA_URJC
* Video básico (url): PON_AQUI_URL_VIDEO_BASICO
* Video parte opcional (url): PON_AQUI_URL_VIDEO_OPCIONAL
* Despliegue (url): PON_AQUI_URL_DESPLIEGUE
* Contraseñas:
  * usuario1 / PON_AQUI_CONTRASEÑA
  * usuario2 / PON_AQUI_CONTRASEÑA
* Cuenta Admin Site: admin / PON_AQUI_CONTRASEÑA_ADMIN

## Recursos implementados y métodos disponibles para cada recurso

* Recurso: /
* Métodos disponibles: GET
* Descripción: Página principal pública de la aplicación.

* Recurso: /accounts/login/
* Métodos disponibles: GET, POST
* Descripción: Página de inicio de sesión.

* Recurso: /accounts/logout/
* Métodos disponibles: POST
* Descripción: Cierre de sesión del usuario autenticado.

* Recurso: /conversations/
* Métodos disponibles: GET
* Descripción: Lista de conversaciones del usuario autenticado.

* Recurso: /conversations/new/
* Métodos disponibles: POST
* Descripción: Crea una nueva conversación para el usuario autenticado.

* Recurso: /conversations/<id>/
* Métodos disponibles: GET
* Descripción: Muestra una conversación concreta y sus mensajes.

* Recurso: /conversations/<id>/send/
* Métodos disponibles: POST
* Descripción: Envía un mensaje a una conversación y actualiza el chat usando HTMX.

* Recurso: /conversations/<id>/delete/
* Métodos disponibles: POST
* Descripción: Borra una conversación propia del usuario autenticado.

* Recurso: /conversations/<id>/rename/
* Métodos disponibles: POST
* Descripción: Cambia el título de una conversación propia del usuario autenticado.

* Recurso: /conversations/<id>/json/
* Métodos disponibles: GET
* Descripción: Devuelve una conversación completa en formato JSON.

* Recurso: /profile/
* Métodos disponibles: GET
* Descripción: Muestra el perfil del usuario, su configuración y sus estadísticas.

* Recurso: /settings/
* Métodos disponibles: GET, POST
* Descripción: Muestra y permite modificar la configuración del usuario.

* Recurso: /help/
* Métodos disponibles: GET
* Descripción: Página de ayuda de la aplicación.

* Recurso: /admin/
* Métodos disponibles: GET, POST
* Descripción: Admin Site de Django.

## Resumen parte obligatoria

ChatIA es una aplicación web hecha con Django que permite a usuarios autenticados mantener conversaciones con una inteligencia artificial.

La aplicación permite crear conversaciones, enviar mensajes, recibir respuestas de un modelo LLM externo y conservar el historial de cada chat en la base de datos. Cada conversación pertenece a un usuario, por lo que cada usuario solo puede ver sus propias conversaciones.

La gestión de sesiones de conversación se ha implementado mediante el modelo `Conversation`. Desde la página de chats, el usuario puede crear conversaciones nuevas, listar sus conversaciones anteriores, entrar en una conversación para recuperar su historial, renombrarla o borrarla.

Los mensajes se guardan mediante el modelo `Message`. Cada mensaje está asociado a una conversación y puede pertenecer al usuario o a la IA.

La aplicación incluye una página de perfil y una página de configuración. Cada usuario tiene un perfil propio mediante el modelo `UserProfile`, donde se guarda su alias, modelo preferido, temperatura y preferencias visuales del chat.

La integración con la IA se realiza mediante una API externa de NVIDIA Build. La clave de la API se gestiona mediante un fichero `.env`, que no debe subirse al repositorio. La temperatura configurada por el usuario se pasa como parámetro en la llamada al modelo.

Se usa HTMX en el envío de mensajes para actualizar la conversación sin recargar toda la página. También se ofrece un recurso JSON que devuelve una conversación completa con sus mensajes.

Todas las páginas salvo la principal están protegidas mediante autenticación de Django. Si un usuario no autenticado intenta acceder a un recurso protegido, se le redirige al formulario de login.

La aplicación usa Bootstrap para la maquetación, CSS propio para personalizar el aspecto y ficheros estáticos para cargar Bootstrap, el logo y el favicon.

También se han añadido tests extremo a extremo para comprobar los principales recursos de la aplicación.

## Lista partes opcionales

* Nombre parte: Favicon e imagen de cabecera

Se ha añadido una imagen propia cargada desde la carpeta `static`. Esta imagen se usa como logo en la cabecera de la aplicación y también como favicon de la pestaña del navegador.

* Nombre parte: Personalización visual del chat por usuario

Cada usuario puede personalizar el aspecto de los mensajes del chat desde la página de configuración. Puede elegir el fondo de sus mensajes, el fondo de los mensajes de la IA, el color de letra y el tipo de letra de los mensajes.

* Nombre parte: Renombrado de conversaciones

Se ha añadido la posibilidad de cambiar el título de una conversación desde la lista de chats. El cambio se realiza mediante POST y solo afecta a conversaciones del usuario autenticado.

* Nombre parte: Borrado de conversaciones

Se ha añadido la posibilidad de borrar conversaciones propias desde la lista de chats. El borrado se realiza mediante POST y con protección CSRF.

* Nombre parte: Limpieza básica de respuestas de la IA

Antes de guardar la respuesta de la IA, se limpian algunos símbolos de Markdown para que el texto se vea mejor en el chat, manteniendo los saltos de línea.

* Nombre parte: Uso real de la temperatura configurada por el usuario

La temperatura guardada en la configuración del usuario se usa en la llamada a la API del modelo LLM, de forma que cada usuario puede ajustar el comportamiento de las respuestas.