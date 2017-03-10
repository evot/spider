Skip to content
This repository
Search
Pull requests
Issues
Gist
 @evot
 Sign out
 Watch 0
  Star 0
  Fork 0 evot/spider
 Code  Issues 0  Pull requests 0  Projects 0  Wiki  Pulse  Graphs  Settings
Branch: master Find file Copy pathspider/zh_ans_spider.py
d66cbd7  just now
@evot evot Update zh_ans_spider.py
1 contributor
RawBlameHistory
129 lines (108 sloc)  3.89 KB
import os
import requests
from lxml import html
from html2text import html2text
from mylog import log


'''
1, get the page source
2, save the page source
3, parse
'''


class Model(object):
    def __repr__(self):
        class_name = self.__class__.__name__
        properties = ('{0} = ({1})'.format(k, v) for k, v in self.__dict__.items())
        return '\n<{0}:\n  {1}\n>'.format(class_name, '\n  '.join(properties))


class Target(Model):
    def __init__(self):
        super(Target, self).__init__()
        self.title = ''
        self.author = ''
        self.url = ''
        self.date = ''
        self.html = ''
        self.content = html2text(self.html)
        self.vote_count = 0


def save(dir_name, generated_targets):
    """save targets to md"""
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    os.chdir(dir_name)
    for targets in generated_targets:
        for t in targets:
            # log(t)
            title = t.title
            url = '[问题链接]({})'.format(t.url)
            if '/' in title:
                title = '每'.join(title.split('/'))
            filename = '{}_{}.md'.format(t.vote_count, title)
            with open(filename, 'w', encoding='utf-8') as f:
                sep = '** 回答 **<hr>'
                ft_list = [t.title,
                           url,
                           t.date,
                           sep,
                           t.content,
                           ]
                log(t.title, t.date, t.url)
                ft = '\n\n'.join(ft_list)
                # log(ft)
                f.write(ft)


def target_from_node(node):
    t = Target()
    special_node = node.xpath('.//a[@class="answer-date-link meta-item"]')
    if len(special_node) > 0:
        date_node = special_node[0]
        t.date = date_node.text
        t.path = node.xpath('.//a[@class="question_link"]')[0].attrib['href']
        t.url = 'https://www.zhihu.com' + t.path
        t.title = node.xpath('.//a[@class="question_link"]/text()')[0].strip()
        t.vote_count = int(node.xpath('.//div[@class="zm-item-vote"]/a/text()')[0])
        t.author = node.xpath('.//a[@class="author-link"]/text()')[0]
        t.html = node.xpath('.//textarea[@class="content"]/text()')[0]
        t.content = html2text(t.html)
    else:
        t.html = '内容被和谐'
        t.content = '内容被和谐'
    return t


def get_page(url):
    headers = {
        'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
        'Host': "www.zhihu.com",
        'Origin': "http://www.zhihu.com",
        'Pragma': "no-cache",
        'Referer': "http://www.zhihu.com/",
        'X-Requested-With': "XMLHttpRequest",
    }
    page = requests.get(url, headers=headers)
    return page


def target_from_url(url):
    # 获取这个网页
    page = get_page(url)
    # 解析成树状节点类型
    root = html.fromstring(page.content)
    # 得到页面内的目标所在节点的列表
    node_list = root.xpath('//div[@class="zm-item"]')
    # log(len(node_list))
    # 对于每个节点, 调用函数 target_from_node 得到一个格式化后的 target
    targets = [target_from_node(node) for node in node_list]
    return targets


def gen_targets(username, page_number):
    for i in range(page_number):
        url = 'https://www.zhihu.com/people/{}/answers?page={}'.format(username, i + 1)
        targets = target_from_url(url)
        yield targets
        # 按点赞数从多到少排序
        # log(targets)
        # targets.sort(key=lambda t: t.vote_count, reverse=True)
        # for target in targets:
        #     log(target.vote_count)


def main():
    username = 'xxxxx'
    answers_number = 1021
    page_number = answers_number // 20 + 1
    generated_targets = gen_targets(username, page_number)
    dir_name = username + ' 的回答'
    save(dir_name, generated_targets)


if __name__ == '__main__':
    main()
