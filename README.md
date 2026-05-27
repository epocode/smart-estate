# 智慧房产探索平台 (Smart Estate)

## 项目简介

基于 Python 构建的智慧房产探索平台，通过采集二手房网站数据，存储到 MySQL 数据库中，对整体房价进行分析和预测，构建可视化房产平台。帮助用户快速了解城市与各区域房源及价格情况，找到合适的房源，辅助房地产投资者寻找投资机会。

## 技术架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                      前端展示层                               │
│   Django Templates + ECharts + Baidu Maps + Bootstrap       │
├─────────────────────────────────────────────────────────────┤
│                      后端服务层                               │
│   Django Web Framework (REST API + Views)                   │
├─────────────────────────────────────────────────────────────┤
│                      数据分析层                               │
│   Pandas + Numpy + Matplotlib + Seaborn + Sklearn           │
├─────────────────────────────────────────────────────────────┤
│                      数据采集层                               │
│   Scrapy + Scrapy-Redis + Requests + XPath                  │
├─────────────────────────────────────────────────────────────┤
│                      数据存储层                               │
│   MySQL + Redis                                             │
└─────────────────────────────────────────────────────────────┘
```

## 功能模块

### 1. 数据采集模块 (`/crawler`)

| 功能 | 说明 |
|------|------|
| 房源数据爬取 | 采集链家/贝壳等平台的二手房数据 |
| 分布式爬虫 | 基于 Scrapy-Redis 实现分布式采集 |
| 数据清洗 | 去重、缺失值处理、格式标准化 |
| 定时更新 | 定期增量更新房源数据 |

**采集字段：**
- 房源标题、价格（总价/单价）
- 所在城市、区域、小区名称
- 户型、面积、朝向、楼层
- 建筑年代、装修情况
- 交通便利度、周边配套设施
- 经纬度坐标（用于地图展示）

### 2. 数据存储模块 (`/database`)

**MySQL 数据库设计：**

```sql
-- 城市表
CREATE TABLE city (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL COMMENT '城市名称',
    province VARCHAR(50) COMMENT '所属省份',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 区域表
CREATE TABLE district (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL COMMENT '区域名称',
    city_id INT NOT NULL,
    FOREIGN KEY (city_id) REFERENCES city(id)
);

-- 小区表
CREATE TABLE community (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '小区名称',
    district_id INT NOT NULL,
    longitude DECIMAL(10, 7) COMMENT '经度',
    latitude DECIMAL(10, 7) COMMENT '纬度',
    build_year INT COMMENT '建筑年代',
    FOREIGN KEY (district_id) REFERENCES district(id)
);

-- 房源表
CREATE TABLE house (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL COMMENT '房源标题',
    community_id INT NOT NULL,
    total_price DECIMAL(10, 2) COMMENT '总价(万元)',
    unit_price DECIMAL(10, 2) COMMENT '单价(元/平米)',
    area DECIMAL(8, 2) COMMENT '面积(平米)',
    layout VARCHAR(50) COMMENT '户型',
    orientation VARCHAR(50) COMMENT '朝向',
    floor VARCHAR(50) COMMENT '楼层',
    decoration VARCHAR(50) COMMENT '装修情况',
    elevator TINYINT COMMENT '是否有电梯',
    listing_date DATE COMMENT '挂牌日期',
    source_url VARCHAR(500) COMMENT '来源链接',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (community_id) REFERENCES community(id)
);

-- 房价预测结果表
CREATE TABLE price_prediction (
    id INT PRIMARY KEY AUTO_INCREMENT,
    district_id INT NOT NULL,
    predict_date DATE COMMENT '预测日期',
    avg_price DECIMAL(10, 2) COMMENT '预测均价',
    trend VARCHAR(20) COMMENT '趋势(上涨/下跌/平稳)',
    confidence DECIMAL(5, 4) COMMENT '置信度',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (district_id) REFERENCES district(id)
);

-- 周边配套表
CREATE TABLE facility (
    id INT PRIMARY KEY AUTO_INCREMENT,
    community_id INT NOT NULL,
    type VARCHAR(50) COMMENT '类型(交通/教育/医疗/商业)',
    name VARCHAR(100) COMMENT '设施名称',
    distance DECIMAL(6, 2) COMMENT '距离(米)',
    FOREIGN KEY (community_id) REFERENCES community(id)
);
```

### 3. 数据分析与挖掘模块 (`/analysis`)

| 分析内容 | 技术方案 |
|----------|----------|
| 房价分布分析 | Pandas + Matplotlib 统计各区域房价分布 |
| 房价趋势分析 | 时间序列分析，展示历史价格走势 |
| 房价影响因素分析 | 相关性分析（面积、楼层、装修等与价格的关系） |
| 房价预测模型 | Sklearn（线性回归、随机森林、XGBoost） |
| 区域热度分析 | 各区域房源数量、成交量统计 |
| 户型偏好分析 | 不同区域热门户型统计 |

**预测模型特征：**
- 面积、户型、楼层、朝向、装修情况
- 所在区域、小区均价
- 建筑年代、是否有电梯
- 周边配套设施数量

### 4. Web 可视化展示模块 (`/web`)

基于 Django 构建，前端使用 ECharts + 百度地图。

**页面规划：**

| 页面 | 路由 | 功能 |
|------|------|------|
| 首页大屏 | `/` | 全国/省级房价概览，核心指标展示 |
| 城市房价 | `/city/<name>/` | 城市各区域房价地图、排行榜 |
| 区域详情 | `/district/<id>/` | 区域房源列表、价格分布图 |
| 房源详情 | `/house/<id>/` | 单个房源详细信息、周边配套 |
| 房价预测 | `/prediction/` | 房价走势预测、投资建议 |
| 数据对比 | `/compare/` | 多区域/多小区房价对比 |
| 房源搜索 | `/search/` | 按条件筛选房源 |

**可视化图表：**
- 房价热力地图（百度地图 + 热力图层）
- 各区域均价柱状图/折线图（ECharts）
- 房价分布饼图/散点图
- 户型占比环形图
- 房价预测趋势图

## 项目目录结构

```
smart-estate/
├── README.md                   # 项目说明文档
├── requirements.txt            # Python 依赖
├── manage.py                   # Django 管理入口
│
├── crawler/                    # 数据采集模块
│   ├── scrapy.cfg
│   ├── estate_spider/
│   │   ├── __init__.py
│   │   ├── settings.py         # Scrapy 配置
│   │   ├── items.py            # 数据模型定义
│   │   ├── pipelines.py        # 数据处理管道(清洗+入库)
│   │   ├── middlewares.py      # 中间件(代理/UA轮换)
│   │   └── spiders/
│   │       ├── __init__.py
│   │       ├── lianjia.py      # 链家爬虫
│   │       └── beike.py        # 贝壳爬虫
│   └── utils/
│       ├── proxy_pool.py       # 代理池
│       └── data_cleaner.py     # 数据清洗工具
│
├── database/                   # 数据库模块
│   ├── migrations/             # 数据库迁移文件
│   ├── init_db.sql             # 数据库初始化脚本
│   └── seed_data.py            # 测试数据填充
│
├── analysis/                   # 数据分析模块
│   ├── __init__.py
│   ├── price_analysis.py       # 房价分析
│   ├── trend_analysis.py       # 趋势分析
│   ├── correlation.py          # 相关性分析
│   ├── prediction/
│   │   ├── __init__.py
│   │   ├── model_train.py      # 模型训练
│   │   ├── model_predict.py    # 模型预测
│   │   └── models/             # 保存训练好的模型
│   └── visualization/
│       ├── charts.py           # Matplotlib/Seaborn 图表生成
│       └── reports.py          # 分析报告生成
│
├── web/                        # Django Web 应用
│   ├── __init__.py
│   ├── settings.py             # Django 配置
│   ├── urls.py                 # 路由配置
│   ├── wsgi.py
│   ├── apps/
│   │   ├── home/               # 首页应用
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── templates/
│   │   ├── house/              # 房源应用
│   │   │   ├── models.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── serializers.py
│   │   │   └── templates/
│   │   ├── analysis/           # 分析展示应用
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── templates/
│   │   └── prediction/         # 预测应用
│   │       ├── views.py
│   │       ├── urls.py
│   │       └── templates/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   │   ├── echarts.min.js
│   │   │   └── bindbindmap_api.js
│   │   └── images/
│   └── templates/
│       ├── base.html           # 基础模板
│       ├── home.html           # 首页大屏
│       ├── city.html           # 城市页面
│       ├── district.html       # 区域页面
│       ├── house_detail.html   # 房源详情
│       ├── prediction.html     # 预测页面
│       ├── compare.html        # 对比页面
│       └── search.html         # 搜索页面
│
├── config/                     # 配置文件
│   ├── database.yml            # 数据库配置
│   └── redis.yml               # Redis 配置
│
├── docs/                       # 项目文档
│   ├── api.md                  # API 文档
│   ├── deployment.md           # 部署文档
│   └── screenshots/            # 截图
│
└── scripts/                    # 工具脚本
    ├── start_crawler.py        # 启动爬虫
    ├── run_analysis.py         # 运行分析
    └── init_project.py         # 项目初始化
```

## 技术栈详情

| 层级 | 技术 | 用途 |
|------|------|------|
| 数据采集 | Scrapy + Scrapy-Redis | 分布式爬虫框架 |
| 数据采集 | Requests + lxml(XPath) | 辅助数据请求与解析 |
| 数据存储 | MySQL 8.0 | 主数据库 |
| 数据存储 | Redis | 爬虫去重 + 分布式调度 |
| 数据存储 | PyMySQL | Python MySQL 驱动 |
| 数据处理 | Pandas | 数据清洗与处理 |
| 数据分析 | Numpy | 数值计算 |
| 数据可视化 | Matplotlib + Seaborn | 静态图表生成 |
| 机器学习 | Scikit-learn | 房价预测模型 |
| Web 框架 | Django 4.x | 后端服务 |
| 前端图表 | ECharts 5.x | 交互式图表 |
| 前端地图 | 百度地图 API | 房源地图展示 |
| 前端 UI | Bootstrap 5 | 响应式页面布局 |
| 前端交互 | JavaScript (原生) | 页面交互逻辑 |

## 开发计划

### 第一阶段：环境搭建与数据采集（1-2 周）
1. 搭建开发环境，安装依赖
2. 设计并创建 MySQL 数据库
3. 开发 Scrapy 爬虫，采集链家二手房数据
4. 实现数据清洗管道，数据入库

### 第二阶段：数据分析与建模（1-2 周）
1. 使用 Pandas 进行数据探索性分析
2. 使用 Matplotlib/Seaborn 生成分析图表
3. 构建房价预测模型（线性回归 + 随机森林）
4. 模型评估与调优

### 第三阶段：Web 平台开发（2-3 周）
1. 搭建 Django 项目结构
2. 开发首页大屏（ECharts 可视化）
3. 开发城市/区域房价展示页面
4. 集成百度地图，实现房源地图展示
5. 开发房价预测展示页面
6. 开发房源搜索与对比功能

### 第四阶段：优化与部署（1 周）
1. 性能优化（数据库索引、缓存）
2. 页面响应式适配
3. 部署上线

## 环境要求

- Python 3.9+（推荐 3.13）
- MySQL 8.0+
- Redis 6.0+
- [uv](https://docs.astral.sh/uv/) — Python 包管理器

## 快速开始

```bash
# 1. 克隆项目
git clone git@github.com:epocode/smart-estate.git
cd smart-estate

# 2. 使用 uv 创建虚拟环境并安装依赖（一步完成）
uv sync

# 3. 配置数据库
# 编辑 config/database.yml，填入 MySQL 连接信息

# 4. 初始化数据库
uv run python scripts/init_project.py

# 5. 填充测试数据（可选）
uv run python database/seed_data.py

# 6. 启动爬虫采集数据
uv run python scripts/start_crawler.py

# 7. 运行数据分析
uv run python scripts/run_analysis.py

# 8. 启动 Web 服务
uv run python manage.py runserver
```

### 常用 uv 命令

```bash
# 添加新依赖
uv add <package>

# 添加开发依赖
uv add --dev <package>

# 更新所有依赖
uv lock --upgrade

# 在虚拟环境中运行任意命令
uv run <command>

# 激活虚拟环境（也可以手动激活后直接用 python）
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
```

## 预期成果

1. **数据层面**：采集多个城市数万条二手房数据
2. **分析层面**：生成房价分布、趋势、影响因素等多维度分析报告
3. **预测层面**：房价预测模型准确率达到 85%+
4. **展示层面**：可视化大屏直观展示全国/城市/区域房价情况
5. **实用层面**：帮助用户快速找到合适房源，辅助投资决策

## 部署方式

### 方式一：本地开发部署（SQLite，零配置）

无需安装 MySQL，适合快速体验和开发调试。项目会自动检测 MySQL 是否可用，不可用时降级为 SQLite。

```bash
# 1. 安装依赖
uv sync

# 2. 数据库迁移
uv run python manage.py migrate

# 3. 填充测试数据
uv run python scripts/seed_django.py

# 4. 启动服务
uv run python manage.py runserver
```

访问 http://127.0.0.1:8000 即可查看。

### 方式二：本地开发部署（MySQL）

适合需要完整功能（爬虫入库、大数据量）的场景。

```bash
# 1. 安装并启动 MySQL 8.0、Redis 6.0

# 2. 修改数据库配置
# 编辑 config/database.yml，填入实际的 MySQL 连接信息
# database:
#   host: 127.0.0.1
#   port: 3306
#   name: smart_estate
#   user: root
#   password: your_actual_password
#   charset: utf8mb4

# 3. 安装依赖
uv sync

# 4. 初始化数据库（创建库和表）
uv run python scripts/init_project.py

# 5. Django 迁移
uv run python manage.py migrate

# 6. 填充测试数据（或运行爬虫采集真实数据）
uv run python scripts/seed_django.py
# 或: uv run python scripts/start_crawler.py --city 北京 --pages 5

# 7. 启动服务
uv run python manage.py runserver
```

### 方式三：生产环境部署（Linux 服务器）

使用 Gunicorn + Nginx 部署，适合对外提供服务。

#### 1. 服务器准备

```bash
# 安装系统依赖
sudo apt update
sudo apt install -y mysql-server redis-server nginx

# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 2. 项目部署

```bash
# 克隆项目
git clone git@github.com:epocode/smart-estate.git /opt/smart-estate
cd /opt/smart-estate

# 安装依赖
uv sync --no-dev

# 配置数据库
cp config/database.yml config/database.yml.bak
# 编辑 config/database.yml 填入生产数据库信息

# 初始化数据库
uv run python scripts/init_project.py
uv run python manage.py migrate

# 收集静态文件
uv run python manage.py collectstatic --noinput
```

#### 3. 配置 Gunicorn

```bash
# 安装 gunicorn
uv add gunicorn

# 启动（开发测试）
uv run gunicorn web.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

创建 systemd 服务文件 `/etc/systemd/system/smart-estate.service`：

```ini
[Unit]
Description=Smart Estate Django App
After=network.target mysql.service redis.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/smart-estate
ExecStart=/opt/smart-estate/.venv/bin/gunicorn web.wsgi:application --bind 127.0.0.1:8000 --workers 4 --timeout 120
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable smart-estate
sudo systemctl start smart-estate
```

#### 4. 配置 Nginx

创建 `/etc/nginx/sites-available/smart-estate`：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /opt/smart-estate/staticfiles/;
        expires 30d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/smart-estate /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 5. 生产环境注意事项

在 `web/settings.py` 中修改以下配置：

```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'your-server-ip']
SECRET_KEY = 'your-production-secret-key'  # 使用随机生成的密钥
```

### 方式四：Docker 部署（可选）

如需容器化部署，可创建 `Dockerfile`：

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 安装依赖
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# 复制项目
COPY . .

# 收集静态文件
RUN uv run python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["uv", "run", "gunicorn", "web.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

配合 `docker-compose.yml`：

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DJANGO_SETTINGS_MODULE=web.settings

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: smart_estate_pwd
      MYSQL_DATABASE: smart_estate
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database/init_db.sql:/docker-entrypoint-initdb.d/init.sql

  redis:
    image: redis:7-alpine

volumes:
  mysql_data:
```

```bash
docker-compose up -d
```

## License

MIT
