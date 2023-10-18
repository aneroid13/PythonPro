import datetime
from urllib.parse import urlparse, unquote
from socket import socket, error, AF_INET, SOCK_STREAM
import argparse
import select
import mimetypes
from queue import Queue
from threading import Thread
import logging
import logging.handlers
from pathlib import Path
import re
from json import load, JSONDecodeError


# from multiprocessing import pool

def server_log_config(log_path):
    log_path = Path(log_path)
    if not log_path.exists():
        log_path.touch()
    fh = logging.handlers.TimedRotatingFileHandler(log_path, 'd', 1, 7, 'utf-8')
    log_format = logging.Formatter('{asctime} {levelname} {module} {message}', style='{')
    fh.setFormatter(log_format)

    ch = logging.StreamHandler()

    logger_srv = logging.getLogger("server_logger")
    logger_srv.setLevel(logging.DEBUG)
    logger_srv.addHandler(fh)
    logger_srv.addHandler(ch)
    return logger_srv


class SenderThread(Thread):
    def __init__(self, workers, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.input_queue = Queue(workers)

    def send(self, item):
        self.input_queue.put(item)

    def close(self):
        self.input_queue.put(None)
        self.input_queue.join()

    def run(self):
        while True:
            item = self.input_queue.get()
            if item is None:
                break
            sock, msg, bodyfile = item

            try:
                sock.send(msg)
                if bodyfile:
                    file = open(bodyfile, "rb")
                    sock.sendfile(file)
                    file.close()
            except error as er:
                log.error(f"Write socket error: {er}")
                sock.close()

            self.input_queue.task_done()

        self.input_queue.task_done()
        return


class HTTPServer:
    def __init__(self, addr="localhost", port=8080, workers=100, root_folder="."):
        self.HTTPAddress = addr
        self.HTTPPort = port
        self.root = Path(root_folder).resolve()
        self.index = "index.html"
        self.srv_socket = None
        self.socket_poll_timeout = 1    # in ms
        self.serve_req = re.compile(r"^[GET|POST|HEAD]+ .* HTTP/1.[0|1]+\r\n.*")
        self.clients = []
        self.to_clients = SenderThread(workers)
        self.textanswers = self.read_conf("./httpcodes.conf")

    def srv_poll(self, mask):
        poller = select.poll()
        poller.register(self.srv_socket.fileno(), mask)
        return poller.poll(self.socket_poll_timeout)

    def clinet_poll(self, sock):
        poller = select.poll()
        poller.register(sock.fileno(), select.POLLIN | select.POLLPRI)
        return poller.poll(self.socket_poll_timeout)

    def read_events(self, sock):
        if sock is self.srv_socket:
            newsocket, (ip, port) = sock.accept()
            self.clients.append({'socket': newsocket, 'ip': ip, 'port': port})

    def client_events(self, sock):
        req_data = sock.recv(1000000)
        req_data = str(req_data.decode('utf-8'))
        if req_data:    #re.match(self.serve_req, req_data):      # Check that request if valid
            self.response(sock, req_data)
        else:
            sock.close()

    def error_events(self, sock):
        log.error("Connection refused or client disconnected")
        select.poller.unregister(sock)
        sock.close()

    def init_server(self):
        self.srv_socket = socket(AF_INET, SOCK_STREAM)
        self.srv_socket.setblocking(0)
        self.srv_socket.bind((self.HTTPAddress, self.HTTPPort))
        self.srv_socket.listen(100)    # connection buffer size

        self.to_clients.start()  # <- New thread coming

    def listen(self):
        while True:
            try:
                events_in = self.srv_poll(select.POLLIN | select.POLLPRI)
                events_err = self.srv_poll(select.POLLERR | select.POLLHUP)

                fd_to_socket = {self.srv_socket.fileno(): self.srv_socket, }
                for fd, flag in events_in:
                    soc = fd_to_socket[fd]
                    self.read_events(soc)

                for fd, flag in events_err:
                    soc = fd_to_socket[fd]
                    self.error_events(soc)

                for client in self.clients:
                    if client['socket']._closed:            # if client['socket'].fileno():
                        self.clients.remove(client)
                        continue
                    else:
                        event_client = self.clinet_poll(client['socket'])
                        fd_to_socket = {client['socket'].fileno(): client['socket'], }

                        for fd, flag in event_client:
                            soc = fd_to_socket[fd]
                            self.client_events(soc)

            except error as ex:
                self.srv_socket.close()
                self.to_clients.close()
                for client in self.clients:
                    client['socket'].close()
                log.error("Error %s", ex)

    def get_req_info(self, data):
        data_splitted = data.split('\n')[0].split(' ')
        method = data_splitted[0]
        path = str(' ').join(data_splitted[1:-1])
        ver = data_splitted[-1]
        return {'method': method, 'path': path, 'version': ver}

    def get_req_headers(self, data):
        headers = data.split('\n')[1:]
        headers = headers.split(':', maxsplit = 1)
        return headers

    def path_read(self, http_path):
        http_path = urlparse(http_path)._replace(query=None).geturl()
        http_path = unquote(http_path)
        req_path = Path(self.root).joinpath("." + http_path)
        req_path = req_path.resolve()
        log.debug(f"Search path: {req_path}")
        if req_path.is_dir():
            req_path = req_path.joinpath(self.index)
        else:
            if str(http_path)[-1] == '/':
                return False
        if req_path.exists() and req_path.is_relative_to(self.root):    # Path exist and not upper than root
            return req_path
        else:
            return False

    def get_headers(self, filepath):
        header = {
                'Date': datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
                'Server': "Python/3.10",
                'Content-Length': 0,
                'Content-Type': '',
                'Connection': 'close'
                 }
        if filepath:
            header['Content-Length'] = Path(filepath).stat().st_size
            mimetypes.add_type("application/x-shockwave-flash", ".swf", True)
            mime = mimetypes.guess_type(filepath)[0]
            if mime:
                header['Content-Type'] = mime
        return "\r\n".join([f"{key}: {val}" for key, val in header.items()])

    def response(self, sock, requset):
        log.debug(requset)
        req = self.get_req_info(requset)
        http_path = self.path_read(req['path'])
        body = None

        if http_path:
            code = 200
            body = http_path
        else:
            code = 404

        if req['method'] == 'HEAD':
            body = None
        elif req['method'] == 'POST':
            code = 405

        http_response = f"HTTP/1.1 {code} {self.textanswers[str(code)]}"
        http_headers = self.get_headers(http_path)
        http_response = "\r\n".join([http_response, http_headers, '\r\n']).encode('utf-8')
        log.debug(f"Server send to: {sock.getpeername()} \f\n Server answer : {http_response}")
        self.to_clients.send((sock, http_response, body))

    def read_conf(self, conf_file: str):
        try:
            with open(conf_file, 'rt') as f_conf:
                #print(load(f_conf))
                return load(f_conf)
        except FileNotFoundError:
            log.error(f"File not found: {conf_file}")
        except JSONDecodeError as ex:
            log.error(f"Wrong format, must be json. {ex}")
        except Exception as ex:
            log.error(str(ex))


def get_args():
    parser = argparse.ArgumentParser(
        description='HTTP Server can be started on custom address and port'
    )
    parser.add_argument('-a', '--address', default="0.0.0.0", required=False, action='store', help='Input ip address')
    parser.add_argument('-p', '--port', default=8080, required=False, action='store', help='Input port')
    parser.add_argument('-w', '--workers', default=500, required=False, action='store', help='Workers')
    parser.add_argument('-r', '--root', default=".", required=False, action='store', help='Root folder')
    return parser.parse_args()


if __name__ == "__main__":
    log = server_log_config("./log/server_log.txt")
    runHTTPrun = HTTPServer(
        str(get_args().address),
        int(get_args().port),
        workers=get_args().workers,
        root_folder=get_args().root
    )
    runHTTPrun.init_server()
    runHTTPrun.listen()
