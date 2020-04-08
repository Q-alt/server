#
# Серверное приложение для соединений
#
import asyncio
from asyncio import transports


class ServerProtocol(asyncio.Protocol):
    login: str = None
    server: 'Server'
    transport: transports.Transport

    def __init__(self, server: 'Server'):
        self.server = server

    def data_received(self, data: bytes):
        print(data)

        decoded = data.decode()

        if self.login is not None:
            self.send_message(decoded)
        else:
            if decoded.startswith("login:")   :
              
                self.login = decoded.replace("login:", "").replace("\r\n", "")
                if not self.login in self.server.clients_name : 
                        self.send_history()
                        self.server.clients_name.append(self.login)
                        self.transport.write(
                               f"Привет, {self.login}!\n".encode()
                )
                else : 
                       self.transport.write(f"Логин {self.login} уже занят, попробуйте другой\n".encode())
                       self.transport.close()
            else:
                self.transport.write("Неправильный логин\n".encode())
                #self.transport.close()
    def connection_made(self, transport: transports.Transport):
        self.server.clients.append(self)
        
        self.transport = transport
        print("Пришел новый клиент")

    def connection_lost(self, exception):
        self.server.clients.remove(self)
        if self.login != None :
            self.server.clients_name.remove(self.login)	
        print("Клиент вышел")

    def send_message(self, content: str):
        message = f"{self.login}: {content}\n"
        if len(self.server.last_messages) < 10 :
        	self.server.last_messages.append([self.login, content])
        else :
        	del self.server.last_messages[0]
        	self.server.last_messages.append([self.login, content])
  
   
        for user in self.server.clients:
            user.transport.write(message.encode())
    
    
    def send_history(self) :
    	for message in self.server.last_messages :
    		self.transport.write(f"{message[0]}: {message[1]}\n".encode())
    	

class Server:
    clients: list
    clients_name: list =[]
    last_messages: list = []

    def __init__(self):
        self.clients = []

    def build_protocol(self):
        return ServerProtocol(self)

    async def start(self):
        loop = asyncio.get_running_loop()

        coroutine = await loop.create_server(
            self.build_protocol,
            '127.0.0.1',
            8888
        )

        print("Сервер запущен ...")

        await coroutine.serve_forever()


process = Server()

try:
    asyncio.run(process.start())
except KeyboardInterrupt:
    print("Сервер остановлен вручную")
    
