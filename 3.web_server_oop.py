#coding=utf-8
import socket
import re, os

file_path = os.path.join(os.path.dirname(__file__), "templates")
bind_addr = ('', 8888)


class WSGIserver(object):
    def __init__(self, bind_addr):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 允许在7788端口资源没有彻底释放完毕时，可以重复绑定7788端口
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(bind_addr)
        self.server_socket.listen(128)

    def run_server(self):
        # 作为程序的主控制入口
        while True:
            self.client_socket, client_addr = self.server_socket.accept()
            self.handle_client()

    def handle_client(self):
        # 为一个客户端进行服务
        recv_data = self.client_socket.recv(1024).decode("utf-8")
        request_header_lines = recv_data.splitlines()
        for line in request_header_lines:
            print(line)

        http_request_line = request_header_lines[0]
        file_name = re.match("[^/]+(/[^ ]*)", http_request_line).group(1)
        print("file_name_1 ==> ", file_name)

        if file_name == "/":
            file_name = file_path + '/index.html'
        else:
            file_name = file_path + file_name

        print("file_name_2 ==> ", file_name)
        try:
            with open(file_name, 'rb') as f:
                response_body = f.read()
        except IOError:
            response_headers = "HTTP/1.1 404 not found\r\n"
            response_headers += "\r\n"
            response_body = "====sorry ,file not found===="
        else:
            # 组织相应 头信息(header)
            response_headers = "HTTP/1.1 200 OK\r\n"  # 200表示找到这个资源
            response_headers += "\r\n"  # 用一个空的行与body进行隔开
        finally:
            # 组织 内容(body)
            # response = response_headers + response_body
            self.client_socket.send(response_headers.encode("utf-8"))
            self.client_socket.send(response_body)
            self.client_socket.close()


if __name__ == "__main__":
    server = WSGIserver(bind_addr)
    server.run_server()
