import socket
import threading
import json


class Server:
    """
    Lớp server
    """
    def __init__(self):
        """
        Hàm dựng
        """
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__connections = list()
        self.__nicknames = list()

    def __user_thread(self, user_id):
        """
        Luồng con của người dùng
         : param user_id: id người dùng
        """
        connection = self.__connections[user_id]
        nickname = self.__nicknames[user_id]
        print('[Server] user', user_id, nickname, 'Join the chat room')
        self.__broadcast(message='user ' + str(nickname) + '(' + str(user_id) + ')' + 'Join the chat room')

        # Lắng nghe thông tin
        while True:
            # noinspection PyBroadException
            try:
                buffer = connection.recv(1024).decode()
                # Phân tích cú pháp thành dữ liệu json
                obj = json.loads(buffer)
                if obj['type'] == 'broadcast':
                    self.__broadcast(obj['sender_id'], obj['message'])
                else:
                    print('[Server] Unable to parse json packet:', connection.getsockname(), connection.fileno())
            except Exception:
                print('[Server] Connection failure:', connection.getsockname(), connection.fileno())
                self.__connections[user_id].close()
                self.__connections[user_id] = None
                self.__nicknames[user_id] = None

    def __broadcast(self, user_id=0, message=''):
        """
          phát sóng
         : param user_id: id người dùng (0 là hệ thống)
         : thông điệp param: nội dung phát sóng
        """
        for i in range(1, len(self.__connections)):
            if user_id != i:
                self.__connections[i].send(json.dumps({
                    'sender_id': user_id,
                    'sender_nickname': self.__nicknames[user_id],
                    'message': message
                }).encode())

    def start(self):
        """
        Khởi động Server
        """

        self.__socket.bind(('localhost', 5768))

        self.__socket.listen(10)
        print('[Server] Server is running......')

        # Xóa kết nối
        self.__connections.clear()
        self.__nicknames.clear()
        self.__connections.append(None)
        self.__nicknames.append('System')

        # Start listening
        while True:
            connection, address = self.__socket.accept()
            print('[Server] Received a new connection', connection.getsockname(), connection.fileno())

            # Nhận dữ liệu
            # noinspection PyBroadException
            try:
                buffer = connection.recv(1024).decode()
                # Phân tích cú pháp thành dữ liệu json
                obj = json.loads(buffer)
                # Nếu đó là lệnh kết nối, thì số người dùng mới được trả về để nhận kết nối người dùng
                if obj['type'] == 'login':
                    self.__connections.append(connection)
                    self.__nicknames.append(obj['nickname'])
                    connection.send(json.dumps({
                        'id': len(self.__connections) - 1
                    }).encode())

                    # Mở một chuỗi mới
                    thread = threading.Thread(target=self.__user_thread, args=(len(self.__connections) - 1, ))
                    thread.setDaemon(True)
                    thread.start()
                else:
                    print('[Server] Unable to parse json packet:', connection.getsockname(), connection.fileno())
            except Exception:
                print('[Server] Unable to accept data:', connection.getsockname(), connection.fileno())
