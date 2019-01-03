#coding=utf-8
import socket
import re, os
import time
import select

templates_path = os.path.join(os.path.dirname(__file__), "templates")
bind_addr = ('', 8888)


class WSGIserver(object):
    def __init__(self, bind_addr, file_path):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 允许在7788端口资源没有彻底释放完毕时，可以重复绑定7788端口
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(bind_addr)
        self.server_socket.listen(128)
        self.server_socket.setblocking(False)

        self.file_path = file_path
        self.client_dict = {}
        self.client_addr = {}
        self.epoll = select.epoll()
        self.epoll.register(self.server_socket, select.EPOLLIN | select.EPOLLET)

    def run_server(self):
        # 作为程序的主控制入口
        while True:
            # epoll 进行 fd 扫描的地方 -- 未指定超时时间则为阻塞等待
            epoll_list = self.epoll.poll()
            # 对事件进行判断
            for fd, events in epoll_list:
                # 如果是socket创建的套接字被激活
                if fd == self.server_socket.fileno():
                    try:
                        new_socket, new_addr = self.server_socket.accept()
                    except Exception as ret:
                        print('mei有新的客户端到来%s', ret)
                    else:
                        print('有新的客户端到来%s' % str(new_addr))
                        # 将 conn 和 addr 信息分别保存起来
                        self.client_dict[new_socket.fileno()] = new_socket
                        self.client_addr[new_socket.fileno()] = new_addr
                        # 向 epoll 中注册 新socket 的 可读 事件
                        self.epoll.register(new_socket.fileno(), select.EPOLLIN | select.EPOLLET)
                # 如果是客户端发送数据
                elif events == select.EPOLLIN:
                    # 从激活 fd 上接收
                    recvData = self.client_dict[fd].recv(1024).decode("utf-8")
                    if recvData:
                        print('recv:%s' % recvData)
                        self.handle_client(self.client_dict[fd], recvData)
                    else:
                        # 从 epoll 中移除该 连接 fd
                        self.epoll.unregister(fd)
                        # server 侧主动关闭该 连接 fd
                        self.client_dict[fd].close()
                        print("%s---offline---" % str(self.client_addr[fd]))
                        del self.client_dict[fd]
                        del self.client_addr[fd]

    def handle_client(self, client_socket, recv_data):
        request_header_lines = recv_data.splitlines()
        for line in request_header_lines:
            print(line)

        http_request_line = request_header_lines[0]
        file_name = re.match("[^/]+(/[^ ]*)", http_request_line).group(1)
        print("file_name_1 ==> ", file_name)

        if file_name == "/":
            file_name = self.file_path + '/index.html'
        else:
            file_name = self.file_path + file_name

        print("file_name_2 ==> ", file_name)
        try:
            with open(file_name, 'rb') as f:
                response_body = f.read()
            # 组织相应 头信息(header)
            response_headers = "HTTP/1.1 200 OK\r\n"  # 200表示找到这个资源
            response_headers += "\r\n"  # 用一个空的行与body进行隔开
        except IOError:
            response_headers = "HTTP/1.1 404 not found\r\n"
            response_headers += "\r\n"
            response_body = "====sorry ,file not found====".encode("utf-8")
        else:
            # 组织 内容(body)
            # response = response_headers + response_body
            client_socket.send(response_headers.encode("utf-8"))
            client_socket.send(response_body)
            client_socket.close()


if __name__ == "__main__":
    server = WSGIserver(bind_addr, templates_path)
    server.run_server()
