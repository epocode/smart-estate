"""
链家二手房爬虫
采集链家网二手房数据
"""
import re
import scrapy
from estate_spider.items import HouseItem


class LianjiaSpider(scrapy.Spider):
    name = 'lianjia'
    allowed_domains = ['lianjia.com']

    # 支持的城市及其链家域名前缀
    CITY_MAP = {
        '北京': 'bj',
        '上海': 'sh',
        '广州': 'gz',
        '深圳': 'sz',
        '杭州': 'hz',
        '成都': 'cd',
        '武汉': 'wh',
        '南京': 'nj',
        '重庆': 'cq',
        '西安': 'xa',
    }

    def __init__(self, city='北京', pages=5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.city = city
        self.pages = int(pages)
        self.city_code = self.CITY_MAP.get(city, 'bj')

    def start_requests(self):
        """生成起始请求"""
        base_url = f'https://{self.city_code}.lianjia.com/ershoufang/pg{{page}}/'
        for page in range(1, self.pages + 1):
            url = base_url.format(page=page)
            yield scrapy.Request(url, callback=self.parse_list, meta={'city': self.city})

    def parse_list(self, response):
        """解析房源列表页"""
        city = response.meta['city']
        house_list = response.xpath('//ul[@class="sellListContent"]/li[@class="clear"]')

        for house in house_list:
            detail_url = house.xpath('.//div[@class="title"]/a/@href').get()
            if detail_url:
                yield scrapy.Request(
                    detail_url,
                    callback=self.parse_detail,
                    meta={'city': city}
                )

    def parse_detail(self, response):
        """解析房源详情页"""
        item = HouseItem()

        item['city'] = response.meta['city']
        item['source_url'] = response.url

        # 标题
        item['title'] = response.xpath('//h1[@class="main"]/text()').get('').strip()

        # 价格
        total_price = response.xpath('//span[@class="total"]/text()').get('')
        item['total_price'] = total_price

        unit_price = response.xpath('//span[@class="unitPriceValue"]/text()').get('')
        item['unit_price'] = unit_price

        # 基本信息
        info_items = response.xpath('//div[@class="base"]//li')
        for info in info_items:
            label = info.xpath('./span/text()').get('')
            value = info.xpath('./text()').get('').strip()

            if '户型' in label:
                item['layout'] = value
            elif '建筑面积' in label:
                item['area'] = value
            elif '朝向' in label or '房屋朝向' in label:
                item['orientation'] = value
            elif '装修' in label:
                item['decoration'] = value
            elif '楼层' in label:
                item['floor'] = value
                # 提取总楼层
                floor_match = re.search(r'共(\d+)层', value)
                if floor_match:
                    item['total_floor'] = floor_match.group(1)
            elif '电梯' in label:
                item['elevator'] = value

        # 位置信息
        area_info = response.xpath('//div[@class="areaName"]//a/text()').getall()
        if len(area_info) >= 1:
            item['district'] = area_info[0].strip()
        if len(area_info) >= 2:
            item['community'] = area_info[1].strip()
        else:
            community = response.xpath('//div[@class="communityName"]//a/text()').get('')
            item['community'] = community.strip()

        # 挂牌日期
        listing_date = response.xpath(
            '//div[@class="transaction"]//li[contains(.,"挂牌时间")]//span[2]/text()'
        ).get('')
        item['listing_date'] = listing_date.strip() if listing_date else None

        # 建筑年代
        build_year = response.xpath(
            '//div[@class="transaction"]//li[contains(.,"建成年代")]//span[2]/text()'
        ).get('')
        if build_year:
            year_match = re.search(r'(\d{4})', build_year)
            if year_match:
                item['house_year'] = int(year_match.group(1))

        yield item
