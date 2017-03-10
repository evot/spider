import socket
import ssl
import sys


class HttpClient(object):
    def __init__(self):
        super(HttpClient, self).__init__()
        self.request = ''
        self.response_header = ''
        self.response_body = ''


client = HttpClient()


def parsed_url(url):
    # 检查协议
    protocol = 'http'
    if url[:7] == 'http://':
        u = url.split('://')[1]
    elif url[:8] == 'https://':
        protocol = 'https'
        u = url.split('://')[1]
    else:
        u = url

    # 检查默认 path
    i = u.find('/')
    if i == -1:
        host = u
        path = '/'
    else:
        host = u[:i]
        path = u[i:]

    # 检查端口
    port_dict = {
        'http': 80,
        'https': 443,
    }
    port = port_dict[protocol]
    if host.find(':') != -1:
        h = host.split(':')
        host = h[0]
        port = int(h[1])

    return protocol, host, port, path


def socket_by_protocol(protocol):
    if protocol == 'http':
        s = socket.socket()
    else:
        s = ssl.wrap_socket(socket.socket())
    return s


def response_by_socket(s):
    response = b''
    buffer_size = 1024
    while True:
        r = s.recv(buffer_size)
        if len(r) == 0:
            break
        response += r
    return response.decode('utf-8')


def parsed_response(r):
    header, body = r.split('\r\n\r\n', 1)
    client.response_header = header
    client.response_body = body
    h = header.split('\r\n')
    status_code = h[0].split()[1]
    status_code = int(status_code)

    headers = {}
    for line in h[1:]:
        k, v = line.split(': ')
        headers[k] = v
    return status_code, headers, body


def request_by(host, path, method, headers, body):
    request_head = '{} {} HTTP/1.1'.format(method, path)
    default_header = {
        'host': host,
        'Connection': 'close',
        'Content-Length': str(len(body)),
        'Content-Type': 'text/html',
        'User - Agent': 'Mozilla / 5.0(Macintosh;IntelMac OS X 10 11_4) '
                        'AppleWebKit / 601.5.17(KHTML, like Gecko) Version / 9.1 Safari / 601.5.17'
    }
    if headers is not None:
        default_header.update(headers)
    head_lines = [request_head] + ['{}: {}'.format(k, v) for k, v in default_header.items()]
    head = '\r\n'.join(head_lines)
    request = '{}\r\n\r\n{}'.format(head, body)
    client.request = request
    return request.encode('utf-8')


def get(url, method='GET', headers=None, body=''):
    protocol, host, port, path = parsed_url(url)

    s = socket_by_protocol(protocol)
    s.connect((host, port))
    request = request_by(host, path, method, headers, body)
    s.send(request)
    response = response_by_socket(s)

    status_code, headers, body = parsed_response(response)

    if status_code == 301:
        url = headers['Location']
        return get(url)

    return status_code, headers, body


def print_help():
    print('用法:')
    print('python3 http_client.py http://www.baidu.com')
    print('python3 http_client.py http://www.baidu.com author=tao&lang=python')
    print('\n')


def main(argv):
    # 从命令行取参数
    argc = len(argv)
    if argc == 1:
        print_help()
        return None
    # 参数组装
    url = argv[1]
    print('debug: url', url)
    if argc > 2:
        method = 'POST'
        body = argv[2]
    elif argc > 1:
        method = 'GET'
        body = ''
    get(url, method, body=body)

    print('下面是发出的 HTTP 请求信息')
    print(client.request)
    print('\n\n下面是服务器响应的 HTTP 头')
    print(client.response_header)
    print('\n\n下面是服务器响应的 body')
    print(client.response_body)


if __name__ == '__main__':
    main(sys.argv)
