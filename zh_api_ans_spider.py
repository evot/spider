import os
import time
import json

import requests
from html2text import html2text

args_dict = {}


class Model(object):

    def __repr__(self):
        class_name = self.__class__.__name__
        properties = ('{0} = ({1})'.format(k, v)
                      for k, v in self.__dict__.items())
        return '\n<{0}:\n  {1}\n>'.format(class_name, '\n  '.join(properties))


class Target(Model):

    def __init__(self):
        super(Target, self).__init__()
        self.title = ''
        self.author = ''
        self.url = ''
        self.created_time = '0'
        self.html = ''
        self.text = html2text(self.html)
        self.voteup_count = 0
        self.date = self.format_time()
        self.sep = '**回答**<hr>'

    def format_time(self):
        sample = '%Y-%m-%d %H:%M:%S'
        data = time.localtime(int(self.created_time))
        dt = time.strftime(sample, data)
        return dt


def set_headers(username):
    referer = 'https://www.zhihu.com/people/{}/answers'.format(username)
    header = {
        'referer': referer
    }
    headers = {
        'Host': 'www.zhihu.com',
        'Connection': 'keep-alive',
        'authorization': '',
        'x-udid': '',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/'
                      '537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
    }
    headers.update(header)
    return headers


def get_page(offset):
    username = args_dict.get('username', '')
    headers = args_dict.get('headers', '')
    url = 'https://www.zhihu.com/api/v4/members/{}/answers?' \
          'sort_by=created&include=data[*].is_normal,suggest_edit,' \
          'comment_count,collapsed_counts,reviewing_comments_count,' \
          'can_comment,content,voteup_count,reshipment_settings,' \
          'comment_permission,mark_infos,created_time,updated_time,' \
          'relationship.voting,is_author,is_thanked,is_nothelp,' \
          'upvoted_followees;data[*].author.badge[?(type=best_answerer)].topics&' \
          'limit=20&offset={}'.format(username, offset)
    r = requests.get(url, headers=headers)
    return r


def data_to_target(data):
    data_dict = data
    question_dict = data_dict.get('question', {})
    author_dict = data_dict.get('author', {})
    question_id = question_dict.get('id', '')
    answer_id = data_dict.get('id', '')
    t = Target()
    t.title = question_dict.get('title', '')
    if '/' in t.title:
        t.title = '每'.join(t.title.split('/'))
    t.author = author_dict.get('name', '')
    t.url = 'https://www.zhihu.com/question/{}/answer/{}'.format(
        question_id, answer_id)
    t.created_time = data_dict.get('created_time', '0')
    t.html = data_dict.get('content', '')
    t.text = html2text(t.html)
    t.voteup_count = data_dict.get('voteup_count', 0)
    return t


def gen_targets(page_num):
    page_dict = load_page(page_num)
    data_list = page_dict.get('data', [])
    # targets = [data_to_target(data) for data in data_list]
    for data in data_list:
        target = data_to_target(data)
        yield target


def save_md(page_num):
    for t in gen_targets(page_num):
        home_dir = args_dict.get('home_dir', '')
        md_name = '{}_{}.md'.format(t.voteup_count, t.title)
        path = home_dir + '/markdown/' + md_name
        ft_list = [
            t.title,
            t.url,
            t.date,
            t.sep,
            t.text,
        ]
        data = '\n\n'.join(ft_list)
        save(path, data)


def save_html(page_num):
    for t in gen_targets(page_num):
        home_dir = args_dict.get('home_dir', '')
        html_name = '{}_{}.html'.format(t.voteup_count, t.title)
        path = home_dir + '/html/' + html_name
        ft_list = [
            t.title,
            t.url,
            t.date,
            t.sep,
            t.html,
        ]
        data = '\n\n'.join(ft_list)
        save(path, data)


def load_page(page_num):
    home_dir = args_dict.get('home_dir', '')
    path = home_dir + '/json/page{}.json'.format(page_num + 1)
    with open(path, 'r') as f:
        return json.loads(f.read())


def save_page(page_num):
    home_dir = args_dict.get('home_dir', '')
    offset = page_num * 20
    r = get_page(offset)
    data = r.text
    path = home_dir + '/json/page{}.json'.format(page_num + 1)
    save(path, data)


def save_all():
    pages = args_dict.get('page_count', -1)
    for page_num in range(pages):
        save_page(page_num)
        save_html(page_num)
        save_md(page_num)


def save(path, data):
    if '/' in path:
        dir_name = '/'.join(path.split('/')[:-1])
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(data)


def gen_args(username):
    # 可以直接由 seed(username) 可以生成的 args1
    generated_args_dict = dict(
        username=username,
        home_dir='{} 的回答'.format(username),
        headers=set_headers(username),
    )
    # 生成下面的 args2 需要上面已经生成的 args1 作为 seed
    args_dict.update(generated_args_dict)

    ans_count = get_ans_count()
    page_count = ans_count // 20 + 1
    args_dict['ans_count'] = ans_count
    args_dict['page_count'] = page_count
    return None


def get_ans_count():
    r = get_page(0)
    data = json.loads(r.text)
    paging = data.get('paging', {})
    ans_count = paging.get('totals', 0)
    return ans_count


def args_seed():
    pass


def main():
    # 登录知乎后获取请求 headers 里的 authorization 和 x-udid 的内容添加到程序中
    username_list = [
        'username',
    ]
    for username in username_list:
        gen_args(username)
        save_all()


if __name__ == '__main__':
    main()
