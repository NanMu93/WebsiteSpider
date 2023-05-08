import scrapy

from scrapy.selector import Selector
from lxml import etree
from lxml import html
from lxml.html.clean import Cleaner

class DemoWebsiteSpider(scrapy.Spider):
    name = "demowebsite"
    allowed_domains = ["www.demowebsite.com", "demowebsite.com"]
    start_urls = ["http://www.demowebsite.com/"]

    def start_requests(self):
        cj_url = ['http://cj.demowebsite.com/ketang/']
#                  'http://cj.demowebsite.com/news/']
        news_urls = ['http://www.demowebsite.com/culture/237146/index.html']
#                     'http://www.demowebsite.com/travel/news/index.html',
#                     'http://www.demowebsite.com/travel/travelnote/index.html',
#                     'http://www.demowebsite.com/travel/column/index.html']
        travel_video_urls = ['http://www.demowebsite.com/travel/video/story/']
#                             'http://www.demowebsite.com/travel/video/person/',
#                             'http://www.demowebsite.com/travel/video/scenery/']
        video_url = 'http://www.demowebsite.com/lens/235128/index.html'
        aiwen_video = 'http://www.demowebsite.com/lens/235131/index.html'
#        for i in news_urls:
#            yield scrapy.Request(url=i, callback=self.second_parse)
        for j in travel_video_urls:
            yield scrapy.Request(url=j, callback=self.card_parse)
#        for k in cj_url:
#            yield scrapy.Request(url=k, callback=self.card_parse)
#        yield scrapy.Request(url=video_url, callback=self.second_parse)
#        yield scrapy.Request(url=aiwen_video, callback=self.aiwen_parse)
        # yield scrapy.Request(url=self.start_urls[0], callback=self.start_parse)

    def start_parse(self, response):
        if response.status == 404:
            self.logger.warning('Page not found: %s', response.url)
        else:
            yield scrapy.Request(url='http://www.demowebsite.com/travel/column/index.html', callback=self.second_parse)

    def second_parse(self, response):
        """
        子栏目列表页面处理
        :param response:
        :return:
        """
        if response.status == 404:
            self.logger.warning('Page not found: %s', response.url)
        else:
            sub_list = response.xpath('/html/body/div[4]/div[1]/dl[@class="item clearfix"]')
            news_list = []
            for i in sub_list:
                try:
                    if '排除来源' in i.css('em.name::text').get():
                        continue
                except TypeError:
                    pass
                news_list.append(News())
                news_list[-1]['link'] = i.xpath('.//a/@href').get()
                news_list[-1]['summary'] = i.css('dd.intro a::text').get()
                if i.xpath('.//img'):
                    news_list[-1]['cover_tag'] = 1
                    news_list[-1]['image_urls'] = [i.xpath('.//img/@src').get()]
            for news in news_list:
                request = scrapy.Request(url=news['link'], callback=self.parse)
                request.cb_kwargs['news'] = news
                yield request
            if response.css('div.tkp_page'):
                if response.css('div.tkp_page div.cms_curpage'):
                    next_url = response.urljoin(response.css('div.tkp_page').xpath('.//a[@class="cms_nextpage"]/@href').get())
                    yield scrapy.Request(url=next_url, callback=self.second_parse)

    def card_parse(self, response):
        """
        卡片列表页面处理
        :param response:
        :return:
        """
        if response.status == 404:
            self.logger.warning('Page not found: %s', response.url)
        else:
            sub_list = response.xpath('/html/body/div[4]/div[1]').css('dl.item')
            news_list = []
            for i in sub_list:
                news_list.append(News())
                news_list[-1]['link'] = i.xpath('.//a/@href').get()
                news_list[-1]['summary'] = i.css('dd.intro a::text').get()
                if i.xpath('.//img'):
                    news_list[-1]['cover_tag'] = 1
                    news_list[-1]['image_urls'] = [i.xpath('.//img/@src').get()]
            for news in news_list:
                request = scrapy.Request(url=news['link'], callback=self.parse)
                request.cb_kwargs['news'] = news
                yield request

    def aiwen_parse(self, response):
        """
        视频demo列表
        :param response:
        :return:
        """
        if response.status == 404:
            self.logger.warning('Page not found: %s', response.url)
        else:
            sub_list = response.css('div.swiper-container a')
            sub_list2 = response.css('dl.item').css('dt')
            news_list = []
            for i in sub_list:
                news_list.append(News())
                news_list[-1]['link'] = i.xpath('@href').get()
                if i.xpath('.//img'):
                    news_list[-1]['cover_tag'] = 1
                    news_list[-1]['image_urls'] = [i.xpath('.//img/@src').get()]
            for j in sub_list2:
                news_list.append(News())
                news_list[-1]['link'] = j.xpath('.//a/@href').get()
                if j.xpath('.//img'):
                    news_list[-1]['cover_tag'] = 1
                    news_list[-1]['image_urls'] = [j.xpath('.//img/@src').get()]
            for news in news_list:
                request = scrapy.Request(url=news['link'], callback=self.parse)
                request.cb_kwargs['news'] = news
                yield request

    def parse(self, response, **cb_kwargs):
        if response.status == 404:
            self.logger.warning('Page not found: %s', response.url)
        else:
            cleaner = Cleaner()
            cleaner.remove_tags = ['a', 'div', 'span', 'style', 'script', 'p', 'strong', 'br', 'center']
            news = cb_kwargs['news']
#            news['content'] = response.css('div.tkp_content').get()
            e1 = html.fromstring(response.css('div.tkp_content').get())
            e3 = html.tostring(e1).decode('utf-8')
            news['content'] = cleaner.clean_html(e3)
            news['title'] = response.css('h2.tkp_con_title::text').get().strip('\ufeff')
            news['publish_time'] = response.css('div.tkp_con_author span::text')[0].get()
            try:
                news['source'] = response.css('div.tkp_con_author span::text')[1].get()
            except IndexError:
                news['source'] = response.xpath('/html/body/div[2]/div[1]/div[1]/text()').get()
            if response.css('div.tkp_content').xpath('.//img'):
                img_list = response.css('div.tkp_content').xpath('.//img/@src')
                for i in img_list:
                    news['image_urls'].append(i.get())
            if response.css('div.tkp_content').xpath('.//video'):
                news['file_urls'] = [response.css('div.tkp_content').xpath('.//video').xpath('.//@src').get(), response.css('div.tkp_content').xpath('.//video/@poster').get()]
            elif response.css('div.video_content'):
                news['file_urls'] = [response.css('div.video_content').xpath('.//@src').get(), response.css('div.video_content').xpath('.//video/@poster').get()]
            if '排除来源' not in news['content']:
                yield news


class News(scrapy.Item):
    # 文章链接
    link = scrapy.Field()
    # 所在栏目
    column = scrapy.Field()
    # 文章标题
    title = scrapy.Field()
    # 发表时间
    publish_time = scrapy.Field()
    # 摘要
    summary = scrapy.Field()
    # 内容
    content = scrapy.Field()
    # 缩略图标记
    cover_tag = scrapy.Field()
    # 图片链接
    image_urls = scrapy.Field()
    # 图片保存路径
    image_paths = scrapy.Field()
    # 图片保存信息
    images = scrapy.Field()
    # 视频链接和视频封面链接
    file_urls = scrapy.Field()
    # 视频保存信息
    files = scrapy.Field()
    # 视频保存信息
    video = scrapy.Field()
    # 来源
    source = scrapy.Field()
