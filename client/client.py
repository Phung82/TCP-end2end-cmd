import socket
import threading
import json
from cmd import Cmd


class Client(Cmd):
    """
    Client
    """
    prompt = ''
    intro = '[Welcome] Simple chat room client (Cli version)\n' + '[Welcome] Type help to get help\n'

    def __init__(self):
        super().__init__()
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__id = None
        self.__nickname = None

    def __receive_message_thread(self):
        """
        Chấp nhận chuỗi tin nhắn
        """
        while True:
            # noinspection PyBroadException
            try:
                buffer = self.__socket.recv(1024).decode()
                obj = json.loads(buffer)
                print('[' + str(obj['sender_nickname']) + '(' + str(obj['sender_id']) + ')' + ']', obj['message'])
            except Exception:
                print('[Client] Unable to get data from the server')

    def __send_message_thread(self, message):
        """
        Gửi chuỗi tin nhắn
          : param message: nội dung tin nhắn
        """
        self.__socket.send(json.dumps({
            'type': 'broadcast',
            'sender_id': self.__id,
            'message': message
        }).encode())

    def start(self):
        """
        Khởi động client
        """
        self.__socket.connect(('localhost', 5768))
        self.cmdloop()

    def do_login(self, args):
        """
        Đăng nhập vào phòng trò chuyện
         : param args: tham số
        """
        nickname = args.split(' ')[0]

        #   Gửi thông tin đến máy chủ để lấy id người dùng
        self.__socket.send(json.dumps({
            'type': 'login',
            'nickname': nickname
        }).encode())
        # Chấp nhận thông tin
        # noinspection PyBroadException
        try:
            buffer = self.__socket.recv(1024).decode()
            obj = json.loads(buffer)
            if obj['id']:
                self.__nickname = nickname
                self.__id = obj['id']
                print('[Client] Successfully logged!')

                # Mở chuỗi con để nhận dữ liệu
                thread = threading.Thread(target=self.__receive_message_thread)
                thread.setDaemon(True)
                thread.start()
            else:
                print('[Client] Unable to login!')
        except Exception:
            print('[Client] Unable to get data from the server')

    def do_send(self, args):
        """
        gửi tin nhắn
         : param args: tham số
        """
        message = args
        # Hiển thị tin nhắn do chính client gửi
        print('[' + str(self.__nickname) + '(' + str(self.__id) + ')' + ']', message)
        # Mở chuỗi con để gửi dữ liệu
        thread = threading.Thread(target=self.__send_message_thread, args=(message, ))
        thread.setDaemon(True)
        thread.start()

    def do_help(self, arg):
        command = arg.split(' ')[0]
        if command == '':
            print('[Help] login nickname - Login to the chat room, nickname is your chosen nickname')
            print('[Help] send message - Send a message, message is the message you entered')
        elif command == 'login':
            print('[Help] login nickname - Login to the chat room, nickname is your chosen nickname')
        elif command == 'send':
            print('[Help] send message - Send a message, message is the message you entered')
        else:
            print('[Help] Did not find the instruction you want to know')
