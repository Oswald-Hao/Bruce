#!/usr/bin/env python3
"""
用户行为分析系统 - User Behavior Analytics
功能：用户行为跟踪、事件记录、漏斗分析、留存分析、用户画像
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid
from collections import defaultdict


# 数据目录
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# 创建必要的目录
os.makedirs(DATA_DIR, exist_ok=True)


class EventType(Enum):
    """事件类型"""
    PAGE_VIEW = "page_view"
    CLICK = "click"
    SCROLL = "scroll"
    FORM_SUBMIT = "form_submit"
    SEARCH = "search"
    ADD_TO_CART = "add_to_cart"
    PURCHASE = "purchase"
    SIGN_UP = "sign_up"
    LOGIN = "login"
    LOGOUT = "logout"


class UserStatus(Enum):
    """用户状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CHURNED = "churned"


@dataclass
class Event:
    """事件"""
    event_id: str
    user_id: str
    event_type: str
    timestamp: str
    properties: Dict = field(default_factory=dict)
    session_id: Optional[str] = None
    page_url: Optional[str] = None
    referrer: Optional[str] = None


@dataclass
class User:
    """用户"""
    user_id: str
    first_seen: str
    last_seen: str
    status: str = UserStatus.ACTIVE.value
    total_events: int = 0
    total_sessions: int = 0
    properties: Dict = field(default_factory=dict)


@dataclass
class Session:
    """会话"""
    session_id: str
    user_id: str
    start_time: str
    end_time: Optional[str] = None
    duration: int = 0
    events_count: int = 0
    page_views: int = 0


@dataclass
class Funnel:
    """漏斗"""
    funnel_id: str
    name: str
    steps: List[Dict] = field(default_factory=list)
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


class EventManager(DataManager):
    """事件管理"""

    def __init__(self):
        super().__init__('events.json')

    def track_event(self, user_id: str, event_type: str, **kwargs) -> Event:
        """记录事件"""
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            event_type=event_type,
            timestamp=datetime.now().isoformat(),
            **kwargs
        )
        self.data.append(asdict(event))
        self.save()
        return event

    def get_user_events(self, user_id: str, event_type: str = None) -> List[Event]:
        """获取用户事件"""
        results = []
        for evt in self.data:
            if evt['user_id'] == user_id:
                if event_type is None or evt['event_type'] == event_type:
                    results.append(Event(**evt))
        return results

    def get_events_by_type(self, event_type: str) -> List[Event]:
        """按类型获取事件"""
        results = []
        for evt in self.data:
            if evt['event_type'] == event_type:
                results.append(Event(**evt))
        return results

    def get_events_in_range(self, start_time: str, end_time: str) -> List[Event]:
        """获取时间范围内的事件"""
        results = []
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)

        for evt in self.data:
            evt_dt = datetime.fromisoformat(evt['timestamp'])
            if start_dt <= evt_dt <= end_dt:
                results.append(Event(**evt))
        return results


class UserManager(DataManager):
    """用户管理"""

    def __init__(self):
        super().__init__('users.json')

    def get_or_create_user(self, user_id: str, **properties) -> User:
        """获取或创建用户"""
        for user in self.data:
            if user['user_id'] == user_id:
                # 更新最后活跃时间
                user['last_seen'] = datetime.now().isoformat()
                user['total_events'] += 1
                self.save()
                return User(**user)

        # 创建新用户
        now = datetime.now().isoformat()
        user = User(
            user_id=user_id,
            first_seen=now,
            last_seen=now,
            properties=properties
        )
        self.data.append(asdict(user))
        self.save()
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """获取用户"""
        for user in self.data:
            if user['user_id'] == user_id:
                return User(**user)
        return None

    def update_user(self, user_id: str, **kwargs) -> bool:
        """更新用户"""
        for i, user in enumerate(self.data):
            if user['user_id'] == user_id:
                self.data[i].update(kwargs)
                self.save()
                return True
        return False

    def list_users(self, **filters) -> List[User]:
        """列出用户"""
        results = []
        for user in self.data:
            match = True
            for key, value in filters.items():
                if key not in user or user[key] != value:
                    match = False
                    break
            if match:
                results.append(User(**user))
        return results

    def get_active_users(self, days: int = 7) -> int:
        """获取活跃用户数"""
        threshold = datetime.now() - timedelta(days=days)
        count = 0
        for user in self.data:
            last_seen = datetime.fromisoformat(user['last_seen'])
            if last_seen >= threshold:
                count += 1
        return count


class SessionManager(DataManager):
    """会话管理"""

    def __init__(self):
        super().__init__('sessions.json')

    def create_session(self, user_id: str) -> Session:
        """创建会话"""
        session = Session(
            session_id=f"sess_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            start_time=datetime.now().isoformat()
        )
        self.data.append(asdict(session))
        self.save()

        # 更新用户的会话数
        user_mgr = UserManager()
        user = user_mgr.get_user(user_id)
        if user:
            user_mgr.update_user(user_id, total_sessions=user.total_sessions + 1)

        return session

    def end_session(self, session_id: str) -> bool:
        """结束会话"""
        for i, session in enumerate(self.data):
            if session['session_id'] == session_id:
                start_time = datetime.fromisoformat(session['start_time'])
                end_time = datetime.now()
                duration = int((end_time - start_time).total_seconds())

                self.data[i]['end_time'] = end_time.isoformat()
                self.data[i]['duration'] = duration
                self.save()
                return True
        return False

    def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        for session in self.data:
            if session['session_id'] == session_id:
                return Session(**session)
        return None

    def get_user_sessions(self, user_id: str) -> List[Session]:
        """获取用户会话"""
        results = []
        for session in self.data:
            if session['user_id'] == user_id:
                results.append(Session(**session))
        return results


class FunnelManager(DataManager):
    """漏斗管理"""

    def __init__(self):
        super().__init__('funnels.json')

    def create_funnel(self, name: str, steps: List[Dict]) -> Funnel:
        """创建漏斗"""
        funnel = Funnel(
            funnel_id=f"funnel_{uuid.uuid4().hex[:8]}",
            name=name,
            steps=steps
        )
        self.data.append(asdict(funnel))
        self.save()
        return funnel

    def get_funnel(self, funnel_id: str) -> Optional[Funnel]:
        """获取漏斗"""
        for funnel in self.data:
            if funnel['funnel_id'] == funnel_id:
                return Funnel(**funnel)
        return None

    def analyze_funnel(self, funnel_id: str, start_time: str, end_time: str) -> Dict:
        """分析漏斗"""
        funnel = self.get_funnel(funnel_id)
        if not funnel:
            return {}

        event_mgr = EventManager()

        # 获取时间范围内的所有用户
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)

        # 分析每一步
        results = []
        step_users = set()

        for i, step in enumerate(funnel.steps):
            step_type = step['event_type']
            events = event_mgr.get_events_by_type(step_type)

            # 过滤时间和额外条件
            matching_events = []
            for evt in events:
                evt_dt = datetime.fromisoformat(evt['timestamp'])
                if start_dt <= evt_dt <= end_dt:
                    # 检查额外条件
                    match = True
                    for key, value in step.get('conditions', {}).items():
                        if evt.properties.get(key) != value:
                            match = False
                            break
                    if match:
                        matching_events.append(evt)

            users_in_step = set(evt.user_id for evt in matching_events)

            if i == 0:
                step_users = users_in_step
            else:
                step_users = step_users & users_in_step

            conversion_rate = len(step_users) / len(users_in_step) * 100 if users_in_step else 0

            results.append({
                'step': step.get('name', step_type),
                'event_type': step_type,
                'users': len(step_users),
                'conversion_rate': round(conversion_rate, 2)
            })

        return {
            'funnel_id': funnel_id,
            'funnel_name': funnel.name,
            'steps': results,
            'total_users': results[0]['users'] if results else 0
        }


class UserBehaviorAnalytics:
    """用户行为分析系统"""

    def __init__(self):
        self.event_mgr = EventManager()
        self.user_mgr = UserManager()
        self.session_mgr = SessionManager()
        self.funnel_mgr = FunnelManager()

    # 事件跟踪
    def track_event(self, user_id: str, event_type: str, **kwargs) -> Event:
        """记录事件"""
        # 确保用户存在
        self.user_mgr.get_or_create_user(user_id)

        # 记录事件
        event = self.event_mgr.track_event(user_id, event_type, **kwargs)

        # 如果有会话ID，更新会话
        session_id = kwargs.get('session_id')
        if session_id:
            session = self.session_mgr.get_session(session_id)
            if session:
                session.events_count += 1
                if event_type == EventType.PAGE_VIEW.value:
                    session.page_views += 1

        return event

    def track_page_view(self, user_id: str, page_url: str, **kwargs) -> Event:
        """记录页面浏览"""
        return self.track_event(user_id, EventType.PAGE_VIEW.value,
                               page_url=page_url, session_id=kwargs.get('session_id'),
                               referrer=kwargs.get('referrer'))

    def track_click(self, user_id: str, **kwargs) -> Event:
        """记录点击"""
        return self.track_event(user_id, EventType.CLICK.value, **kwargs)

    def track_purchase(self, user_id: str, amount: float, **kwargs) -> Event:
        """记录购买"""
        return self.track_event(user_id, EventType.PURCHASE.value,
                               properties={'amount': amount}, **kwargs)

    # 会话管理
    def create_session(self, user_id: str) -> Session:
        """创建会话"""
        return self.session_mgr.create_session(user_id)

    def end_session(self, session_id: str) -> bool:
        """结束会话"""
        return self.session_mgr.end_session(session_id)

    # 漏斗分析
    def create_funnel(self, name: str, steps: List[Dict]) -> Funnel:
        """创建漏斗"""
        return self.funnel_mgr.create_funnel(name, steps)

    def analyze_funnel(self, funnel_id: str, start_time: str, end_time: str) -> Dict:
        """分析漏斗"""
        return self.funnel_mgr.analyze_funnel(funnel_id, start_time, end_time)

    # 用户分析
    def get_user_profile(self, user_id: str) -> Dict:
        """获取用户画像"""
        user = self.user_mgr.get_user(user_id)
        if not user:
            return {}

        events = self.event_mgr.get_user_events(user_id)
        sessions = self.session_mgr.get_user_sessions(user_id)

        # 事件统计
        event_types = defaultdict(int)
        for evt in events:
            event_types[evt.event_type] += 1

        # 会话统计
        total_duration = sum(s.duration for s in sessions if s.duration > 0)
        avg_duration = total_duration / len(sessions) if sessions else 0

        return {
            'user_id': user.user_id,
            'first_seen': user.first_seen,
            'last_seen': user.last_seen,
            'status': user.status,
            'total_events': user.total_events,
            'total_sessions': user.total_sessions,
            'event_types': dict(event_types),
            'total_duration': total_duration,
            'avg_session_duration': round(avg_duration, 2)
        }

    # 综合分析
    def get_daily_stats(self, days: int = 7) -> Dict:
        """获取每日统计"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        total_users = len(self.user_mgr.data)
        active_users = self.user_mgr.get_active_users(days)
        total_events = len(self.event_mgr.data)

        # 新用户数
        new_users = 0
        for user in self.user_mgr.data:
            first_seen = datetime.fromisoformat(user['first_seen'])
            if first_seen >= start_date:
                new_users += 1

        return {
            'period': f'{days} days',
            'total_users': total_users,
            'active_users': active_users,
            'new_users': new_users,
            'total_events': total_events,
            'avg_events_per_user': round(total_events / total_users, 2) if total_users > 0 else 0
        }

    def get_retention_analysis(self, day0_date: str, return_days: int = 7) -> Dict:
        """留存分析"""
        day0_dt = datetime.fromisoformat(day0_date)
        day1_dt = day0_dt + timedelta(days=1)

        # Day 0 的用户
        day0_users = set()
        for user in self.user_mgr.data:
            first_seen = datetime.fromisoformat(user['first_seen'])
            if first_seen.date() == day0_dt.date():
                day0_users.add(user['user_id'])

        if not day0_users:
            return {'message': 'No users on day 0'}

        # 计算留存
        retention = {}
        for day in range(1, return_days + 1):
            check_date = day0_dt + timedelta(days=day)
            retained = 0

            for user_id in day0_users:
                user = self.user_mgr.get_user(user_id)
                if user:
                    last_seen = datetime.fromisoformat(user['last_seen'])
                    if last_seen >= check_date:
                        retained += 1

            retention_rate = retained / len(day0_users) * 100
            retention[f'Day {day}'] = {
                'retained': retained,
                'rate': round(retention_rate, 2)
            }

        return {
            'day0_date': day0_date,
            'day0_users': len(day0_users),
            'retention': retention
        }


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("用户行为分析系统 - User Behavior Analytics")
        print("\n使用方法:")
        print("  python3 behavior.py track --user_id <用户ID> --event <事件类型>")
        print("  python3 behavior.py page_view --user_id <用户ID> --url <页面URL>")
        print("  python3 behavior.py purchase --user_id <用户ID> --amount <金额>")
        print("  python3 behavior.py create_session --user_id <用户ID>")
        print("  python3 behavior.py user_profile --user_id <用户ID>")
        print("  python3 behavior.py daily_stats --days <天数>")
        print("  python3 behavior.py retention --day0 <日期>")
        return

    system = UserBehaviorAnalytics()
    command = sys.argv[1]

    # 解析参数
    def get_arg(name, default=None):
        idx = sys.argv.index(name) if name in sys.argv else -1
        return sys.argv[idx + 1] if idx >= 0 else default

    try:
        if command == "track":
            user_id = get_arg("--user_id")
            event_type = get_arg("--event")
            if not user_id or not event_type:
                print("错误: 需要用户ID和事件类型")
                return

            event = system.track_event(user_id, event_type)
            print(f"✅ 事件记录成功")
            print(f"   事件ID: {event.event_id}")
            print(f"   用户ID: {user_id}")
            print(f"   事件类型: {event_type}")

        elif command == "page_view":
            user_id = get_arg("--user_id")
            url = get_arg("--url")
            if not user_id or not url:
                print("错误: 需要用户ID和页面URL")
                return

            event = system.track_page_view(user_id, url)
            print(f"✅ 页面浏览记录成功")
            print(f"   页面URL: {url}")

        elif command == "purchase":
            user_id = get_arg("--user_id")
            amount = get_arg("--amount")
            if not user_id or not amount:
                print("错误: 需要用户ID和金额")
                return

            event = system.track_purchase(user_id, float(amount))
            print(f"✅ 购买记录成功")
            print(f"   金额: ¥{amount}")

        elif command == "create_session":
            user_id = get_arg("--user_id")
            if not user_id:
                print("错误: 需要用户ID")
                return

            session = system.create_session(user_id)
            print(f"✅ 会话创建成功")
            print(f"   会话ID: {session.session_id}")

        elif command == "user_profile":
            user_id = get_arg("--user_id")
            if not user_id:
                print("错误: 需要用户ID")
                return

            profile = system.get_user_profile(user_id)
            if profile:
                print(f"📊 用户画像:")
                print(f"   用户ID: {profile['user_id']}")
                print(f"   首次访问: {profile['first_seen']}")
                print(f"   最后活跃: {profile['last_seen']}")
                print(f"   状态: {profile['status']}")
                print(f"   总事件数: {profile['total_events']}")
                print(f"   总会话数: {profile['total_sessions']}")
                print(f"   事件类型分布: {profile['event_types']}")
                print(f"   总时长: {profile['total_duration']}秒")
                print(f"   平均会话时长: {profile['avg_session_duration']}秒")
            else:
                print(f"❌ 用户未找到")

        elif command == "daily_stats":
            days = int(get_arg("--days", 7))
            stats = system.get_daily_stats(days)
            print(f"📊 {stats['period']}统计:")
            print(f"   总用户数: {stats['total_users']}")
            print(f"   活跃用户: {stats['active_users']}")
            print(f"   新用户: {stats['new_users']}")
            print(f"   总事件数: {stats['total_events']}")
            print(f"   平均每用户事件数: {stats['avg_events_per_user']}")

        elif command == "retention":
            day0 = get_arg("--day0")
            if not day0:
                print("错误: 需要日期")
                return

            retention = system.get_retention_analysis(day0)
            if 'message' in retention:
                print(f"{retention['message']}")
            else:
                print(f"📊 留存分析:")
                print(f"   日期: {retention['day0_date']}")
                print(f"   Day 0用户数: {retention['day0_users']}")
                print(f"   留存情况:")
                for day, data in retention['retention'].items():
                    print(f"   {day}: {data['retained']}人 ({data['rate']}%)")

        else:
            print(f"❌ 未知命令: {command}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
