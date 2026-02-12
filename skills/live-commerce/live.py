#!/usr/bin/env python3
"""
直播电商助手 - Live Streaming E-commerce Assistant
功能：直播监控、商品管理、互动分析、数据分析
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid


# 数据目录
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'config')

# 创建必要的目录
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)


class LiveStatus(Enum):
    """直播状态"""
    LIVE = "live"
    ENDED = "ended"
    SCHEDULED = "scheduled"


class ProductStatus(Enum):
    """商品状态"""
    ONLINE = "online"
    OFFLINE = "offline"


class ChatType(Enum):
    """弹幕类型"""
    QUESTION = "question"
    COMMENT = "comment"
    PRAISE = "praise"
    COMPLAINT = "complaint"


class Sentiment(Enum):
    """情感倾向"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


@dataclass
class Product:
    """商品"""
    product_id: str
    name: str
    price: float
    stock: int
    category: Optional[str] = None
    description: Optional[str] = None
    images: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    status: str = ProductStatus.OFFLINE.value
    original_price: Optional[float] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    sales_count: int = 0
    click_count: int = 0
    conversion_rate: float = 0.0


@dataclass
class LiveRecord:
    """直播记录"""
    live_id: str
    room_id: str
    platform: str
    title: str
    start_time: str
    end_time: Optional[str] = None
    status: str = LiveStatus.LIVE.value
    max_viewers: int = 0
    avg_viewers: int = 0
    total_views: int = 0
    interaction_count: int = 0
    sales_amount: float = 0.0
    products: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Viewer:
    """观众"""
    viewer_id: str
    room_id: str
    join_time: str
    platform: str
    leave_time: Optional[str] = None
    watch_duration: int = 0
    is_follower: bool = False
    interactions: int = 0
    purchases: int = 0
    profile: Dict = field(default_factory=dict)


@dataclass
class Chat:
    """弹幕"""
    chat_id: str
    room_id: str
    user_id: str
    username: str
    content: str
    timestamp: str
    type: str = ChatType.COMMENT.value
    replied: bool = False
    sentiment: str = Sentiment.NEUTRAL.value


@dataclass
class AlertRule:
    """提醒规则"""
    rule_id: str
    type: str  # stock, price, activity
    threshold: Any
    message: str
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RecommendRule:
    """推荐规则"""
    rule_id: str
    product_id: str
    keywords: List[str]
    reply: str
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class DataManager:
    """数据管理基类"""

    def __init__(self, filename: str):
        self.filepath = os.path.join(DATA_DIR, filename)
        self.data: List[Dict] = []
        self.load()

    def load(self):
        """加载数据"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"加载数据失败: {e}")
                self.data = []

    def save(self):
        """保存数据"""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存数据失败: {e}")


class ProductManager(DataManager):
    """商品管理"""

    def __init__(self):
        super().__init__('products.json')

    def add_product(self, name: str, price: float, stock: int, **kwargs) -> Product:
        """添加商品"""
        product = Product(
            product_id=f"prod_{uuid.uuid4().hex[:8]}",
            name=name,
            price=price,
            stock=stock,
            **kwargs
        )
        self.data.append(asdict(product))
        self.save()
        return product

    def get_product(self, product_id: str) -> Optional[Product]:
        """获取商品"""
        for prod in self.data:
            if prod['product_id'] == product_id:
                return Product(**prod)
        return None

    def update_product(self, product_id: str, **kwargs) -> bool:
        """更新商品"""
        for i, prod in enumerate(self.data):
            if prod['product_id'] == product_id:
                self.data[i].update(kwargs)
                self.save()
                return True
        return False

    def adjust_price(self, product_id: str, new_price: float) -> bool:
        """调整价格"""
        return self.update_product(product_id, price=new_price)

    def change_stock(self, product_id: str, delta: int) -> bool:
        """改变库存"""
        product = self.get_product(product_id)
        if product:
            new_stock = max(0, product.stock + delta)
            return self.update_product(product_id, stock=new_stock)
        return False

    def list_products(self, **filters) -> List[Product]:
        """列出商品"""
        results = []
        for prod in self.data:
            match = True
            for key, value in filters.items():
                if key not in prod or prod[key] != value:
                    match = False
                    break
            if match:
                results.append(Product(**prod))
        return results

    def record_click(self, product_id: str) -> bool:
        """记录点击"""
        product = self.get_product(product_id)
        if product:
            new_clicks = product.click_count + 1
            self.update_product(product_id, click_count=new_clicks)
            return True
        return False

    def record_sale(self, product_id: str, quantity: int = 1) -> bool:
        """记录销售"""
        product = self.get_product(product_id)
        if product and product.stock >= quantity:
            new_sales = product.sales_count + quantity
            new_stock = product.stock - quantity
            self.update_product(
                product_id,
                sales_count=new_sales,
                stock=new_stock
            )
            return True
        return False

    def get_product_stats(self, product_id: str) -> Dict:
        """获取商品统计"""
        product = self.get_product(product_id)
        if product:
            return {
                'product_id': product.product_id,
                'name': product.name,
                'price': product.price,
                'stock': product.stock,
                'sales_count': product.sales_count,
                'click_count': product.click_count,
                'conversion_rate': product.conversion_rate,
                'total_revenue': product.sales_count * product.price
            }
        return {}


class LiveManager(DataManager):
    """直播管理"""

    def __init__(self):
        super().__init__('lives.json')

    def create_live(self, room_id: str, platform: str, title: str, **kwargs) -> LiveRecord:
        """创建直播"""
        live = LiveRecord(
            live_id=f"live_{uuid.uuid4().hex[:8]}",
            room_id=room_id,
            platform=platform,
            title=title,
            start_time=datetime.now().isoformat(),
            **kwargs
        )
        self.data.append(asdict(live))
        self.save()
        return live

    def get_live(self, live_id: str) -> Optional[LiveRecord]:
        """获取直播"""
        for live in self.data:
            if live['live_id'] == live_id:
                return LiveRecord(**live)
        return None

    def get_live_by_room(self, room_id: str, status: str = None) -> Optional[LiveRecord]:
        """根据房间号获取直播"""
        for live in self.data:
            if live['room_id'] == room_id:
                if status is None or live['status'] == status:
                    return LiveRecord(**live)
        return None

    def update_live(self, live_id: str, **kwargs) -> bool:
        """更新直播"""
        for i, live in enumerate(self.data):
            if live['live_id'] == live_id:
                self.data[i].update(kwargs)
                self.save()
                return True
        return False

    def end_live(self, live_id: str) -> bool:
        """结束直播"""
        return self.update_live(
            live_id,
            end_time=datetime.now().isoformat(),
            status=LiveStatus.ENDED.value
        )

    def add_product_to_live(self, live_id: str, product_id: str) -> bool:
        """添加商品到直播"""
        live = self.get_live(live_id)
        if live and product_id not in live.products:
            live.products.append(product_id)
            return self.update_live(live_id, products=live.products)
        return False

    def record_interaction(self, live_id: str) -> bool:
        """记录互动"""
        live = self.get_live(live_id)
        if live:
            new_count = live.interaction_count + 1
            return self.update_live(live_id, interaction_count=new_count)
        return False

    def record_viewers(self, live_id: str, current_viewers: int) -> bool:
        """记录观看人数"""
        live = self.get_live(live_id)
        if live:
            updates = {
                'max_viewers': max(live.max_viewers, current_viewers),
                'total_views': live.total_views + current_viewers
            }
            return self.update_live(live_id, **updates)
        return False

    def list_lives(self, **filters) -> List[LiveRecord]:
        """列出直播"""
        results = []
        for live in self.data:
            match = True
            for key, value in filters.items():
                if key not in live or live[key] != value:
                    match = False
                    break
            if match:
                results.append(LiveRecord(**live))
        return results


class ViewerManager(DataManager):
    """观众管理"""

    def __init__(self):
        super().__init__('viewers.json')

    def add_viewer(self, room_id: str, user_id: str, **kwargs) -> Viewer:
        """添加观众"""
        viewer = Viewer(
            viewer_id=f"viewer_{uuid.uuid4().hex[:8]}",
            room_id=room_id,
            user_id=user_id,
            join_time=datetime.now().isoformat(),
            **kwargs
        )
        self.data.append(asdict(viewer))
        self.save()
        return viewer

    def get_viewer(self, viewer_id: str) -> Optional[Viewer]:
        """获取观众"""
        for viewer in self.data:
            if viewer['viewer_id'] == viewer_id:
                return Viewer(**viewer)
        return None

    def update_viewer(self, viewer_id: str, **kwargs) -> bool:
        """更新观众"""
        for i, viewer in enumerate(self.data):
            if viewer['viewer_id'] == viewer_id:
                self.data[i].update(kwargs)
                self.save()
                return True
        return False

    def record_leave(self, viewer_id: str) -> bool:
        """记录离开"""
        viewer = self.get_viewer(viewer_id)
        if viewer:
            join_time = datetime.fromisoformat(viewer.join_time)
            leave_time = datetime.now()
            duration = int((leave_time - join_time).total_seconds())
            return self.update_viewer(
                viewer_id,
                leave_time=leave_time.isoformat(),
                watch_duration=duration
            )
        return False

    def record_interaction(self, viewer_id: str) -> bool:
        """记录互动"""
        viewer = self.get_viewer(viewer_id)
        if viewer:
            new_count = viewer.interactions + 1
            return self.update_viewer(viewer_id, interactions=new_count)
        return False

    def record_purchase(self, viewer_id: str) -> bool:
        """记录购买"""
        viewer = self.get_viewer(viewer_id)
        if viewer:
            new_count = viewer.purchases + 1
            return self.update_viewer(viewer_id, purchases=new_count)
        return False

    def list_viewers(self, **filters) -> List[Viewer]:
        """列出观众"""
        results = []
        for viewer in self.data:
            match = True
            for key, value in filters.items():
                if key not in viewer or viewer[key] != value:
                    match = False
                    break
            if match:
                results.append(Viewer(**viewer))
        return results


class ChatManager(DataManager):
    """弹幕管理"""

    def __init__(self):
        super().__init__('chats.json')

    def add_chat(self, room_id: str, user_id: str, username: str, content: str, **kwargs) -> Chat:
        """添加弹幕"""
        chat = Chat(
            chat_id=f"chat_{uuid.uuid4().hex[:8]}",
            room_id=room_id,
            user_id=user_id,
            username=username,
            content=content,
            timestamp=datetime.now().isoformat(),
            **kwargs
        )
        self.data.append(asdict(chat))
        self.save()
        return chat

    def get_chats(self, room_id: str, **filters) -> List[Chat]:
        """获取弹幕"""
        results = []
        for chat in self.data:
            if chat['room_id'] == room_id:
                match = True
                for key, value in filters.items():
                    if key not in chat or chat[key] != value:
                        match = False
                        break
                if match:
                    results.append(Chat(**chat))
        return results

    def get_hot_topics(self, room_id: str, limit: int = 10) -> List[Dict]:
        """获取热门话题"""
        chats = self.get_chats(room_id)
        # 简单关键词提取
        topic_count = {}
        for chat in chats:
            words = chat.content.split()
            for word in words:
                if len(word) > 1:  # 忽略单字
                    topic_count[word] = topic_count.get(word, 0) + 1

        # 排序
        sorted_topics = sorted(topic_count.items(), key=lambda x: x[1], reverse=True)
        return [
            {'topic': topic, 'count': count}
            for topic, count in sorted_topics[:limit]
        ]


class LiveCommerceSystem:
    """直播电商系统主类"""

    def __init__(self):
        self.product_mgr = ProductManager()
        self.live_mgr = LiveManager()
        self.viewer_mgr = ViewerManager()
        self.chat_mgr = ChatManager()

    # 商品管理
    def add_product(self, name: str, price: float, stock: int, **kwargs) -> Product:
        return self.product_mgr.add_product(name, price, stock, **kwargs)

    def adjust_price(self, product_id: str, new_price: float) -> bool:
        return self.product_mgr.adjust_price(product_id, new_price)

    def change_stock(self, product_id: str, delta: int) -> bool:
        return self.product_mgr.change_stock(product_id, delta)

    def list_products(self, **filters) -> List[Product]:
        return self.product_mgr.list_products(**filters)

    def get_product_stats(self, product_id: str) -> Dict:
        return self.product_mgr.get_product_stats(product_id)

    def record_click(self, product_id: str) -> bool:
        return self.product_mgr.record_click(product_id)

    def record_sale(self, product_id: str, quantity: int = 1) -> bool:
        return self.product_mgr.record_sale(product_id, quantity)

    # 直播管理
    def create_live(self, room_id: str, platform: str, title: str, **kwargs) -> LiveRecord:
        return self.live_mgr.create_live(room_id, platform, title, **kwargs)

    def end_live(self, live_id: str) -> bool:
        return self.live_mgr.end_live(live_id)

    def add_product_to_live(self, live_id: str, product_id: str) -> bool:
        return self.live_mgr.add_product_to_live(live_id, product_id)

    def record_interaction(self, live_id: str) -> bool:
        return self.live_mgr.record_interaction(live_id)

    def record_viewers(self, live_id: str, current_viewers: int) -> bool:
        return self.live_mgr.record_viewers(live_id, current_viewers)

    def get_live_stats(self, live_id: str) -> Dict:
        """获取直播统计"""
        live = self.live_mgr.get_live(live_id)
        if live:
            return {
                'live_id': live.live_id,
                'title': live.title,
                'platform': live.platform,
                'start_time': live.start_time,
                'status': live.status,
                'max_viewers': live.max_viewers,
                'avg_viewers': live.avg_viewers,
                'total_views': live.total_views,
                'interaction_count': live.interaction_count,
                'sales_amount': live.sales_amount,
                'products_count': len(live.products)
            }
        return {}

    # 观众管理
    def add_viewer(self, room_id: str, user_id: str, **kwargs) -> Viewer:
        return self.viewer_mgr.add_viewer(room_id, user_id, **kwargs)

    def record_leave(self, viewer_id: str) -> bool:
        return self.viewer_mgr.record_leave(viewer_id)

    def record_viewer_interaction(self, viewer_id: str) -> bool:
        return self.viewer_mgr.record_interaction(viewer_id)

    def record_viewer_purchase(self, viewer_id: str) -> bool:
        return self.viewer_mgr.record_purchase(viewer_id)

    def get_viewer_profile(self, room_id: str) -> Dict:
        """获取观众画像"""
        viewers = self.viewer_mgr.list_viewers(room_id=room_id)

        total_viewers = len(viewers)
        followers = sum(1 for v in viewers if v.is_follower)
        total_interactions = sum(v.interactions for v in viewers)
        total_purchases = sum(v.purchases for v in viewers)

        # 观看时长分析
        durations = [v.watch_duration for v in viewers if v.watch_duration > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0

        return {
            'room_id': room_id,
            'total_viewers': total_viewers,
            'followers_count': followers,
            'followers_rate': round(followers / total_viewers * 100, 2) if total_viewers > 0 else 0,
            'total_interactions': total_interactions,
            'avg_interactions_per_viewer': round(total_interactions / total_viewers, 2) if total_viewers > 0 else 0,
            'total_purchases': total_purchases,
            'purchase_rate': round(total_purchases / total_viewers * 100, 2) if total_viewers > 0 else 0,
            'avg_watch_duration': round(avg_duration, 2)
        }

    # 弹幕管理
    def add_chat(self, room_id: str, user_id: str, username: str, content: str, **kwargs) -> Chat:
        return self.chat_mgr.add_chat(room_id, user_id, username, content, **kwargs)

    def get_chats(self, room_id: str, **filters) -> List[Chat]:
        return self.chat_mgr.get_chats(room_id, **filters)

    def get_hot_topics(self, room_id: str, limit: int = 10) -> List[Dict]:
        return self.chat_mgr.get_hot_topics(room_id, limit)

    # 综合分析
    def conversion_funnel(self, live_id: str) -> Dict:
        """转化漏斗分析"""
        live = self.live_mgr.get_live(live_id)
        if not live:
            return {}

        viewers = self.viewer_mgr.list_viewers(room_id=live.room_id)
        chats = self.chat_mgr.get_chats(live.room_id)

        total_viewers = len(viewers)
        interaction_viewers = sum(1 for v in viewers if v.interactions > 0)
        purchasing_viewers = sum(1 for v in viewers if v.purchases > 0)

        # 商品点击和购买
        total_clicks = 0
        total_purchases = 0
        for prod_id in live.products:
            prod = self.product_mgr.get_product(prod_id)
            if prod:
                total_clicks += prod.click_count
                total_purchases += prod.sales_count

        return {
            'live_id': live_id,
            'room_id': live.room_id,
            'total_viewers': total_viewers,
            'interaction_viewers': interaction_viewers,
            'interaction_rate': round(interaction_viewers / total_viewers * 100, 2) if total_viewers > 0 else 0,
            'purchasing_viewers': purchasing_viewers,
            'purchase_rate': round(purchasing_viewers / total_viewers * 100, 2) if total_viewers > 0 else 0,
            'total_clicks': total_clicks,
            'click_rate': round(total_clicks / total_viewers * 100, 2) if total_viewers > 0 else 0,
            'total_purchases': total_purchases,
            'conversion_rate': round(total_purchases / total_clicks * 100, 2) if total_clicks > 0 else 0
        }

    def live_summary(self, live_id: str) -> Dict:
        """直播总览"""
        live = self.live_mgr.get_live(live_id)
        if not live:
            return {}

        viewer_profile = self.get_viewer_profile(live.room_id)
        conversion = self.conversion_funnel(live_id)

        return {
            'live': self.get_live_stats(live_id),
            'viewer_profile': viewer_profile,
            'conversion': conversion
        }


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("直播电商助手 - Live Streaming E-commerce Assistant")
        print("\n使用方法:")
        print("  python3 live.py add_product --name <商品名称> --price <价格> --stock <库存>")
        print("  python3 live.py adjust_price --product_id <商品ID> --new_price <新价格>")
        print("  python3 live.py create_live --room_id <房间号> --platform <平台> --title <标题>")
        print("  python3 live.py live_stats --live_id <直播ID>")
        print("  python3 live.py product_stats --product_id <商品ID>")
        print("  python3 live.py conversion_funnel --live_id <直播ID>")
        print("  python3 live.py live_summary --live_id <直播ID>")
        print("  python3 live.py hot_topics --room_id <房间号>")
        return

    system = LiveCommerceSystem()
    command = sys.argv[1]

    # 解析参数
    def get_arg(name, default=None):
        idx = sys.argv.index(name) if name in sys.argv else -1
        return sys.argv[idx + 1] if idx >= 0 else default

    try:
        if command == "add_product":
            name = get_arg("--name")
            price = get_arg("--price")
            stock = get_arg("--stock")
            if not name or not price or not stock:
                print("错误: 需要商品名称、价格和库存")
                return

            product = system.add_product(
                name=name,
                price=float(price),
                stock=int(stock),
                category=get_arg("--category"),
                description=get_arg("--description")
            )
            print(f"✅ 商品创建成功")
            print(f"   商品ID: {product.product_id}")
            print(f"   商品名称: {product.name}")
            print(f"   价格: ¥{product.price}")
            print(f"   库存: {product.stock}")

        elif command == "adjust_price":
            product_id = get_arg("--product_id")
            new_price = get_arg("--new_price")
            if not product_id or not new_price:
                print("错误: 需要商品ID和新价格")
                return

            success = system.adjust_price(product_id, float(new_price))
            if success:
                print(f"✅ 价格调整成功")
            else:
                print(f"❌ 商品未找到")

        elif command == "list_products":
            filters = {}
            if "--category" in sys.argv:
                filters['category'] = get_arg("--category")
            if "--status" in sys.argv:
                filters['status'] = get_arg("--status")

            products = system.list_products(**filters)
            print(f"📋 找到 {len(products)} 个商品:")
            for prod in products[:10]:
                print(f"   - {prod.product_id}: {prod.name} ¥{prod.price} (库存: {prod.stock})")

        elif command == "product_stats":
            product_id = get_arg("--product_id")
            if not product_id:
                print("错误: 需要商品ID")
                return

            stats = system.get_product_stats(product_id)
            if stats:
                print(f"📊 商品统计:")
                print(f"   商品名称: {stats['name']}")
                print(f"   价格: ¥{stats['price']}")
                print(f"   当前库存: {stats['stock']}")
                print(f"   销量: {stats['sales_count']}")
                print(f"   点击数: {stats['click_count']}")
                print(f"   转化率: {stats['conversion_rate']}%")
                print(f"   总收入: ¥{stats['total_revenue']}")
            else:
                print(f"❌ 商品未找到")

        elif command == "create_live":
            room_id = get_arg("--room_id")
            platform = get_arg("--platform")
            title = get_arg("--title")
            if not room_id or not platform or not title:
                print("错误: 需要房间号、平台和标题")
                return

            live = system.create_live(
                room_id=room_id,
                platform=platform,
                title=title
            )
            print(f"✅ 直播创建成功")
            print(f"   直播ID: {live.live_id}")
            print(f"   房间号: {live.room_id}")
            print(f"   平台: {live.platform}")
            print(f"   标题: {live.title}")

        elif command == "end_live":
            live_id = get_arg("--live_id")
            if not live_id:
                print("错误: 需要直播ID")
                return

            success = system.end_live(live_id)
            if success:
                print(f"✅ 直播已结束")
            else:
                print(f"❌ 直播未找到")

        elif command == "live_stats":
            live_id = get_arg("--live_id")
            if not live_id:
                print("错误: 需要直播ID")
                return

            stats = system.get_live_stats(live_id)
            if stats:
                print(f"📊 直播统计:")
                print(f"   标题: {stats['title']}")
                print(f"   平台: {stats['platform']}")
                print(f"   状态: {stats['status']}")
                print(f"   峰值观看: {stats['max_viewers']}")
                print(f"   平均观看: {stats['avg_viewers']}")
                print(f"   总观看: {stats['total_views']}")
                print(f"   互动数: {stats['interaction_count']}")
                print(f"   销售额: ¥{stats['sales_amount']}")
                print(f"   商品数: {stats['products_count']}")
            else:
                print(f"❌ 直播未找到")

        elif command == "add_chat":
            room_id = get_arg("--room_id")
            user_id = get_arg("--user_id")
            username = get_arg("--username")
            content = get_arg("--content")
            if not room_id or not user_id or not username or not content:
                print("错误: 需要房间号、用户ID、用户名和内容")
                return

            chat = system.add_chat(room_id, user_id, username, content)
            print(f"✅ 弹幕记录成功")
            print(f"   弹幕ID: {chat.chat_id}")

        elif command == "hot_topics":
            room_id = get_arg("--room_id")
            if not room_id:
                print("错误: 需要房间号")
                return

            topics = system.get_hot_topics(room_id, limit=10)
            print(f"🔥 热门话题 (房间: {room_id}):")
            for i, topic in enumerate(topics[:10], 1):
                print(f"   {i}. {topic['topic']}: {topic['count']}次")

        elif command == "conversion_funnel":
            live_id = get_arg("--live_id")
            if not live_id:
                print("错误: 需要直播ID")
                return

            funnel = system.conversion_funnel(live_id)
            if funnel:
                print(f"📊 转化漏斗分析:")
                print(f"   总观看人数: {funnel['total_viewers']}")
                print(f"   互动人数: {funnel['interaction_viewers']}")
                print(f"   互动率: {funnel['interaction_rate']}%")
                print(f"   购买人数: {funnel['purchasing_viewers']}")
                print(f"   购买率: {funnel['purchase_rate']}%")
                print(f"   商品点击数: {funnel['total_clicks']}")
                print(f"   点击率: {funnel['click_rate']}%")
                print(f"   总购买数: {funnel['total_purchases']}")
                print(f"   转化率: {funnel['conversion_rate']}%")
            else:
                print(f"❌ 直播未找到")

        elif command == "live_summary":
            live_id = get_arg("--live_id")
            if not live_id:
                print("错误: 需要直播ID")
                return

            summary = system.live_summary(live_id)
            if summary and summary.get('live'):
                print(f"📊 直播总览:")
                print(f"\n   直播数据:")
                live = summary['live']
                print(f"   - 标题: {live['title']}")
                print(f"   - 峰值观看: {live['max_viewers']}")
                print(f"   - 互动数: {live['interaction_count']}")
                print(f"   - 销售额: ¥{live['sales_amount']}")

                if summary.get('viewer_profile'):
                    profile = summary['viewer_profile']
                    print(f"\n   观众画像:")
                    print(f"   - 总观众: {profile['total_viewers']}")
                    print(f"   - 粉丝数: {profile['followers_count']}")
                    print(f"   - 粉丝率: {profile['followers_rate']}%")
                    print(f"   - 购买数: {profile['total_purchases']}")
                    print(f"   - 购买率: {profile['purchase_rate']}%")

                if summary.get('conversion'):
                    conv = summary['conversion']
                    print(f"\n   转化漏斗:")
                    print(f"   - 观看→互动: {conv['interaction_rate']}%")
                    print(f"   - 观看→购买: {conv['purchase_rate']}%")
                    print(f"   - 点击→购买: {conv['conversion_rate']}%")
            else:
                print(f"❌ 直播未找到")

        else:
            print(f"❌ 未知命令: {command}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
