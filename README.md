![Python](https://img.shields.io/badge/python-3.12-blue)
![uv](https://img.shields.io/badge/uses-uv-FF6C37?logo=python)

![MCP Cliente](image/mcp-client.png)

# Creación de un MCP a través de cliente.
Este repositorio contiene una implementación funcional de un **cliente MCP (Model Context Protocol)** que se conecta a un servidor local o remoto y permite interactuar con herramientas externas mediante modelos como **Claude de Anthropic**.

El código ha sido adaptado y extendido a partir del ejemplo oficial de MCP disponible en:  
🔗 [modelcontextprotocol.io/quickstart/client](https://modelcontextprotocol.io/quickstart/client)

## 🚀 ¿Qué es MCP?

**Model Context Protocol (MCP)** es un protocolo abierto para conectar modelos de lenguaje con herramientas y entornos de ejecución. Este cliente permite:

- Conectarse a un servidor MCP que exponga herramientas (por ejemplo, APIs del tiempo).
- Usar modelos como Claude para resolver consultas del usuario.
- Ejecutar herramientas de forma dinámica si el modelo lo decide.

---

## 🏗️ Estructura del Cliente

- **`MCPClient`**: Clase principal que gestiona:
  - Conexión al servidor MCP.
  - Comunicación con el modelo Claude.
  - Ejecución de herramientas y procesamiento de respuestas.
- **`connect_to_server`**: Establece conexión con un script `.py` o `.js` que actúa como servidor MCP.
- **`process_query`**: Envía la consulta al modelo, detecta si quiere usar una herramienta y ejecuta la llamada.
- **`chat_loop`**: Interfaz de consola para enviar consultas de forma interactiva.

---

## ⚙️ Requisitos

- Python 3.10+
- Cuenta y API key de [Anthropic](https://www.anthropic.com/)
- Un servidor MCP (ej. script Python o JS que defina herramientas)

Instala las dependencias:

Debemos de crear un entorno virutal para poder descargar ahí las librerías que fueran necesarias y tenerlo en un lugar "aislado para nuestro trabajo".
```shell
uv init mcp-client
#Entramos en la carpeta que nos ha creado
cd mcp-client

#Creamos el entorno virtual
uv venv

#Activamos el entorno virtual en Windows
.venv/Script/activate

#Instalamos los recursos necesarios
uv add mcp anthropic python-dotenv
```

Crearemos un archivo de nombre ```client.py``` con el siguiente código en Windowds:
```shell
New-Item client.py
```

```shell
uv add mcp anthropic python-dotenv
```

Es aconsejable porque no lo vamos a utilizar quitar el ```main.py``` que nos crea por defecto.

Para el trabajo y la parte de API con Anthropic en este caso también sería útil utilizar un ```.env``` y guardar ahí las claves.

```shell
New-Item .env
```

para poner en marcha el proyecto en la terminal deberas poner:

```shell
uv run .\client.py ..\weather\weather.py
```
Aquí tenemos un uv run .\client.py para arrancar pero necesita un segundo atributo que es el servidor que hayamos creado que en este caso usamos el del tiempo de EEUU que creamos anteriormente.

## Proyecto de cliente

Este proyecto viene junto con el creado de MCP también de conexión rápida sobre [el tiempo de EEUU](https://github.com/pichu2707/mcp-weather) que he dejado el enlace, es decir, sería aconsejable empezar si esto está siendo un comienzo para ti en la introducción de los MCP que vayas primero a ese repositorio y lo descargues.