import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


#1 Inicialización del cliente:
# Esta clase MCPClient se inicializa con la gestión de sesiones y los clientes de API.
class MCPClient:
    # Vamos a crear una clase de cliente básica para el cliente de Anthropic y el MCP
    def __init__(self):
        """
        Pareparamos una sesión MCP vacía y un cliente de Anthropic.
        Usamos AsyncExitStack para majera los contextos de entrada y salida.
        """
        # Iniciamos la sesión y el cliente de Anthropic
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.Anthropic = Anthropic()
    
    #Los métedos vendrán aquí, que serán con los que nos conectamos a un servidor MCP
    async def connect_to_server(self, server_script_path: str):
        """Conectamos un servidor de MCP detectando el script del servidor si es python (.py) o javascript (.js).
        Una vez detectado lanza python o node según el caso.
        Abre el canal de comunicación con el servidor y lo conecta al cliente de Anthropic a través de studio.
        Inicia con el ClietnSession y el cliente de Anthropic.
        Las lista muestra las herramientas disponibles en el servidor MCP.
        Args:
            server_script_path (str): path al script del servidor MCP que puede ser un script de python o un script de javascript
        """
        is_python = server_script_path.endswith('.py')
        is_javascript = server_script_path.endswith('.js')
        if not ( is_python or is_javascript):
            raise ValueError("El script del servidor debe ser un archivo .py o .js")
        
        command = "python" if is_python else "node"
        # Creamos el comando para ejecutar el servidor MCP
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None,
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(
                server_params
            )
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(
                self.stdio,
                self.write,
            )
        )

        # Conectamos el cliente de Anthropic al servidor MCP            
        await self.session.initialize()

        # Lista de herramientas disponibles
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConectando al servidor MCP con herramientas disponibles: ", [tool.name for tool in tools])

        #Ahora agregamos la funcionalidad principal para procesar consulas y manejar las llamadas a las herramientas

    async def process_query(self, query: str) -> str:
        """
        Procesando consulta usando Claude y herramientas disponibles
        Se crea el mensaje del usuario y se envía la consulta a CLoud junto con esas herramientas (tools).
        Interpreta la respuesta:
            - Si es un texto, lo gurada
            - Si es  una herramienta (tool_use), se ejecuta mendiante call_tool.
        Informamos a Claude del resultardo (tool_result) y se guarda la respuesta final.
        Args:
            query (str): Cadena de consulta a procesar

        Returns:
            str: Nos devolverá la respuesta de la consulta procesada
        """
        messages = [
            {
                "role": "user",
                "content": query,
            }
        ]

        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        #Iniciando llamada a Claude API
        response = self.Anthropic.messages.create(
            model="cladude-3-5-sonnet-220241022",
            max_tokens=1000,
            messages=messages,
            tools=available_tools,
        )

        # Procesando la respuesta y gestionar las llamadas a las herramientas
        final_text = []

        assistant_message_content = []
        for content in response.content:
            if content.type == "text":
                final_text.append(content.text)
                assistant_message_content.append(content)
            elif content.type == "tool_use":
                tool_name = content.name
                tool_args = content.input

                # Llamar a la herramienta
                result = await self.session.call_tool(tool_name, tool_args)
                final_text.append(f"[Llamando a la herramienta {tool_name} con los argumentos {tool_args}]")

                assistant_message_content.append(content)
                messages.append({
                    "role": "assistant",
                    "content": assistant_message_content
                })

                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": result.content,
                        }
                    ]
                })

                # Obtener la respuesta final de Claude
                response = self.Anthropic.message.create(
                    model = "claude-3-5-sonnet-220241022",
                    max_tokens=1000,
                    messages=messages,
                    tools=available_tools,
                )

                final_text.append(response.content[0].text)
        return "\n".join(final_text)
    
    #Ahora vamos a agregar el blucle para el chat y las funciones de cierre
    async def chat_loop(self):
        """
        Correr un bucle de chat para el cliente MCP
        Escucha las consultas del usuario y las procesa (input()).
        Procesa cada consulta con el método process_query y muestra la respuesta.
        si el usuario escribe 'quit', se sale del bucle.
        """
        print("\n Cliente Iniciaado...!!!")
        print("Escribe tus consultas y presiona Enter para enviar. Escribe 'quit' para salir.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == "quit":
                    break

                response= await self.process_query(query)
                print(f"\nRespuesta: {response}")
            
            except Exception as e:
                print(f"Error: {str(e)}")

    async def cleanup(self):
        """Limpiar la sesión y cerrar el cliente MCP (exit_stack.aclose()) y muestra el mensaje de despedida"""
        await self.exit_stack.aclose()
        print("Cliente cerrado. Hasta luego...!!!")

        #Por último, agregamos la lógica de ejecución principal:
async def main():
    """
    Ejecuta el script MCP desde (sys.argb[1])
    Lanzal el cliente, conecta y ejecuta el chat
    """
    if len(sys.argv) < 2:
        print("Uso: python cliente.py <ruta_al_script_servidor>")       
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())
