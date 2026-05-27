"""
Item pipelines for data cleaning and storage.
"""
import re
import pymysql
from scrapy.exceptions import DropItem


class DataCleanPipeline:
    """数据清洗管道"""

    def process_item(self, item, spider):
        # 标题不能为空
        if not item.get('title'):
            raise DropItem("Missing title")

        # 清洗价格
        if item.get('total_price'):
            try:
                item['total_price'] = float(re.sub(r'[^\d.]', '', str(item['total_price'])))
            except (ValueError, TypeError):
                item['total_price'] = None

        if item.get('unit_price'):
            try:
                item['unit_price'] = float(re.sub(r'[^\d.]', '', str(item['unit_price'])))
            except (ValueError, TypeError):
                item['unit_price'] = None

        # 清洗面积
        if item.get('area'):
            try:
                item['area'] = float(re.sub(r'[^\d.]', '', str(item['area'])))
            except (ValueError, TypeError):
                item['area'] = None

        # 清洗楼层
        if item.get('total_floor'):
            try:
                item['total_floor'] = int(re.sub(r'[^\d]', '', str(item['total_floor'])))
            except (ValueError, TypeError):
                item['total_floor'] = None

        # 标准化装修情况
        decoration = item.get('decoration', '')
        if '精' in str(decoration):
            item['decoration'] = '精装'
        elif '简' in str(decoration):
            item['decoration'] = '简装'
        elif '毛坯' in str(decoration):
            item['decoration'] = '毛坯'
        else:
            item['decoration'] = '其他'

        # 电梯处理
        elevator = item.get('elevator', '')
        item['elevator'] = 1 if '有' in str(elevator) else 0

        return item


class MySQLPipeline:
    """MySQL 存储管道"""

    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.conn = None
        self.cursor = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST', '127.0.0.1'),
            port=crawler.settings.getint('MYSQL_PORT', 3306),
            user=crawler.settings.get('MYSQL_USER', 'root'),
            password=crawler.settings.get('MYSQL_PASSWORD', ''),
            database=crawler.settings.get('MYSQL_DATABASE', 'smart_estate'),
        )

    def open_spider(self, spider):
        self.conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
        )
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        if self.conn:
            self.conn.close()

    def process_item(self, item, spider):
        try:
            # 获取或创建城市
            city_id = self._get_or_create_city(item.get('city', '未知'))
            # 获取或创建区域
            district_id = self._get_or_create_district(item.get('district', '未知'), city_id)
            # 获取或创建小区
            community_id = self._get_or_create_community(
                item.get('community', '未知'),
                district_id,
                item.get('longitude'),
                item.get('latitude'),
                item.get('house_year'),
            )

            # 插入房源数据
            sql = """
                INSERT INTO house (title, community_id, total_price, unit_price, area,
                    layout, orientation, floor, total_floor, decoration, elevator,
                    listing_date, house_year, source_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(sql, (
                item.get('title'),
                community_id,
                item.get('total_price'),
                item.get('unit_price'),
                item.get('area'),
                item.get('layout'),
                item.get('orientation'),
                item.get('floor'),
                item.get('total_floor'),
                item.get('decoration'),
                item.get('elevator', 0),
                item.get('listing_date'),
                item.get('house_year'),
                item.get('source_url'),
            ))
            self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            spider.logger.error(f"Error saving item: {e}")

        return item

    def _get_or_create_city(self, name):
        self.cursor.execute("SELECT id FROM city WHERE name = %s", (name,))
        result = self.cursor.fetchone()
        if result:
            return result['id']

        self.cursor.execute("INSERT INTO city (name) VALUES (%s)", (name,))
        self.conn.commit()
        return self.cursor.lastrowid

    def _get_or_create_district(self, name, city_id):
        self.cursor.execute(
            "SELECT id FROM district WHERE name = %s AND city_id = %s",
            (name, city_id)
        )
        result = self.cursor.fetchone()
        if result:
            return result['id']

        self.cursor.execute(
            "INSERT INTO district (name, city_id) VALUES (%s, %s)",
            (name, city_id)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def _get_or_create_community(self, name, district_id, longitude=None, latitude=None, build_year=None):
        self.cursor.execute(
            "SELECT id FROM community WHERE name = %s AND district_id = %s",
            (name, district_id)
        )
        result = self.cursor.fetchone()
        if result:
            return result['id']

        self.cursor.execute(
            "INSERT INTO community (name, district_id, longitude, latitude, build_year) VALUES (%s, %s, %s, %s, %s)",
            (name, district_id, longitude, latitude, build_year)
        )
        self.conn.commit()
        return self.cursor.lastrowid
