import requests
from lxml import html


class Model(object):
    def __repr__(self):
        class_name = self.__class__.__name__
        properties = ('{} = ({})'.format(k, v) for k, v in self.__dict__.items())
        return '\n<{}:\n  {}\n>'.format(class_name, '\n  '.join(properties))


class Movie(Model):
    def __init__(self):
        super(Movie, self).__init__()
        self.name = ''
        self.score = 0
        self.quote = ''
        self.cover_url = ''


def movie_from_div(div):
    movie = Movie()
    movie.name = div.xpath('.//span[@class="title"]')[0].text
    movie.score = div.xpath('.//span[@class="rating_num"]')[0].text
    movie.quote = div.xpath('.//span[@class="inq"]')[0].text
    img_url = div.xpath('.//div[@class="pic"]/a/img/@src')[0]
    print(img_url)
    movie.cover_url = img_url
    return movie


def movies_from_url(url):
    page = requests.get(url)
    root = html.fromstring(page.content)
    movie_divs = root.xpath('//div[@class="item"]')
    movies = []
    for div in movie_divs:
        movie = movie_from_div(div)
        movies.append(movie)
    return movies


def download_img(url, name):
    r = requests.get(url)
    with open(name, 'wb') as f:
        f.write(r.content)


def save_covers(movies):
    for m in movies:
        download_img(m.cover_url, m.name + '.jpg')


def main():
    url = 'https://movie.douban.com/top250'
    movies = movies_from_url(url)
    print(movies)
    save_covers(movies)


if __name__ == '__main__':
    main()
