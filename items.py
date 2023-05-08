# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


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
    # images保存信息
    images = scrapy.Field()
    # 来源
    source = scrapy.Field()

