import ssl
import socket


def parsed_url(url):
    # 获取host和path
    if (url[:7] == 'http://') or (url[:8] == 'https://'):
        u = url.split('://')[1]
    else:
        u = url
    i = u.find('/')
    if i == -1:
        host = u
        path = '/'
    else:
        host = u[:i]
        path = u[i:]

    # 设置http和https的默认端口
    if url.startswith('https://'):
        port = 443
    else:
        port = 80
        # print('url debug', url, host)
    # 检查端口是否指定
    if ':' in host:
        h = host.split(':')
        host = h[0]
        port = int(h[1])
    return host, port, path


def get(url):
    host, port, path = parsed_url(url)
    s = socket.socket()
    if port == 443:
        s = ssl.wrap_socket(socket.socket())
    s.connect((host, port))
    request = 'GET {} HTTP/1.1\r\nhost:{}\r\nConnection: close\r\n\r\n'.format(path, host)
    encoding = 'utf-8'
    s.send(request.encode(encoding))

    response = b''
    buffer_size = 1024
    while True:
        r = s.recv(buffer_size)
        if len(r):
            response += r
        else:
            break

    response = response_handler(response.decode(encoding))
    return response


def response_handler(response):
    d = '\r\n'
    head = response.split(d, 1)[0]
    if '301' in head:
        # 提取重定向的url并请求
        redirected_url = find(response, 'Location: ', end_label='\r\n')
        response = get(redirected_url)
    return response


def find(item, begin_label, end_label='</span>'):
    begin = item.find(begin_label)
    end = item.find(end_label, begin)
    value = item[begin + len(begin_label):end]
    # print('debug: begin & end',begin, end)
    if begin == -1 or end == -1:
        return None
    return value


def get_data(item):
    index = find(item, '<em class="">', end_label='</em>')
    name = find(item, '<span class="title">')  # chrome审查看的这里为'<span class="title"> ' 多了一个空格
    # print('debug: name', name)
    score = find(item, '<span class="rating_num" property="v:average">')
    numbers = find(item, '<span>')
    quote = find(item, '<span class="inq">')
    if quote is None:
        quote = '无'
    return index, name, score, numbers, quote


def parsed_html(html):
    movie = html.split('<ol class="grid_view">', 1)[1]
    list = movie.split('</ol>', 1)[0]
    # 去掉最后一个为空的 item
    items = list.split('</li>')[:-1]
    return items


def save_data():
    data = ''
    for page in range(10):
        num = page * 25
        url = 'https://movie.douban.com/top250?start={}&filter='.format(num)
        r = get(url)
        html = r.split('\r\n\r\n')[1]
        items = parsed_html(html)
        info = '****** 第{}页   网址: {}  ******\r\n'.format(page + 1, url)
        data += info
        for item in items:
            index, name, score, numbers, quote = get_data(item)
            content = '{}  电影名: {}   分数: {}  {} 引用语: {} \r\n'.format(index, name, score, numbers, quote)
            data += content
        separator = '\r\n\r\n'
        data += separator
    with open('电影.txt', 'wb') as f:
        f.write(data.encode('utf-8'))
    print('250部电影的简要信息已保存至movie.txt, 快查看吧 :)')


def main():
    save_data()


if __name__ == '__main__':
    main()
