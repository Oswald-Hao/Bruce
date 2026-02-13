#!/usr/bin/env python3
"""
API网关和微服务管理系统 - API Gateway and Microservice Manager
提供API路由、负载均衡、限流、认证、监控等功能
"""

import json
import time
import uuid
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime, timedelta
from collections import defaultdict
import re


@dataclass
class Route:
    """路由定义"""
    path: str
    method: str  # GET, POST, PUT, DELETE
    target_url: str
    service_name: str
    timeout: int = 30
    retry_count: int = 3
    rate_limit: int = 100  # 每分钟请求数
    auth_required: bool = False
    enabled: bool = True

    def match(self, path: str, method: str) -> bool:
        """检查是否匹配请求"""
        if self.method != method and self.method != "*":
            return False

        # 简单路径匹配（支持通配符）
        if self.path == "*" or self.path == path:
            return True

        # 支持路径参数，如 /users/{id}
        pattern = self.path.replace("{id}", r"\d+")
        pattern = pattern.replace("{userId}", r"\w+")
        pattern = pattern.replace("*", ".*")

        return re.match(pattern, path) is not None


@dataclass
class Service:
    """微服务定义"""
    name: str
    url: str
    health_check_url: str = "/health"
    health_check_interval: int = 30  # 秒
    weight: int = 100  # 负载均衡权重
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.status = "healthy"
        self.last_health_check = 0
        self.failure_count = 0


@dataclass
class APIRequest:
    """API请求"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    path: str = ""
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    body: Any = None
    query_params: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class APIResponse:
    """API响应"""
    request_id: str = ""
    status_code: int = 200
    headers: Dict[str, str] = field(default_factory=dict)
    body: Any = None
    duration: float = 0.0
    service: str = ""


class RateLimiter:
    """限流器 - 令牌桶算法"""

    def __init__(self, rate: int, per: int = 60):
        self.rate = rate  # 令牌生成速率
        self.per = per  # 时间窗口（秒）
        self.tokens = {}  # {key: {tokens: int, last_update: float}}

    def _get_bucket(self, key: str) -> Dict[str, float]:
        """获取或创建令牌桶"""
        now = time.time()

        if key not in self.tokens:
            self.tokens[key] = {"tokens": self.rate, "last_update": now}
            return self.tokens[key]

        bucket = self.tokens[key]

        # 重新计算令牌数
        elapsed = now - bucket["last_update"]
        new_tokens = elapsed * (self.rate / self.per)
        bucket["tokens"] = min(self.rate, bucket["tokens"] + new_tokens)
        bucket["last_update"] = now

        return bucket

    def check(self, key: str, consume: int = 1) -> bool:
        """检查是否有足够令牌"""
        bucket = self._get_bucket(key)

        if bucket["tokens"] >= consume:
            bucket["tokens"] -= consume
            return True

        return False

    def reset(self, key: str):
        """重置令牌桶"""
        if key in self.tokens:
            del self.tokens[key]


class AuthManager:
    """认证管理器"""

    def __init__(self):
        self.api_keys: Dict[str, Dict[str, Any]] = {}
        self.jwt_secret = "default_secret_key"

    def generate_api_key(self, client_id: str, scopes: List[str] = None) -> str:
        """生成API密钥"""
        api_key = f"sk_{hashlib.sha256(f'{client_id}{time.time()}'.encode()).hexdigest()[:32]}"

        self.api_keys[api_key] = {
            "client_id": client_id,
            "scopes": scopes or [],
            "created_at": time.time(),
            "last_used": 0
        }

        return api_key

    def validate_api_key(self, api_key: str) -> bool:
        """验证API密钥"""
        return api_key in self.api_keys

    def validate_token(self, token: str) -> Dict[str, Any]:
        """验证JWT令牌（简化版）"""
        # 实际实现应该使用jwt库
        if token and token.startswith("Bearer "):
            token = token[7:]

        # 简化的令牌验证
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return {"valid": False}

            return {"valid": True, "user_id": "user_123"}
        except:
            return {"valid": False}

    def check_scope(self, api_key: str, required_scope: str) -> bool:
        """检查权限范围"""
        if api_key not in self.api_keys:
            return False

        scopes = self.api_keys[api_key]["scopes"]
        return "*" in scopes or required_scope in scopes


class LoadBalancer:
    """负载均衡器"""

    def __init__(self, strategy: str = "round_robin"):
        self.strategy = strategy
        self.current_index = 0

    def select(self, services: List[Service]) -> Optional[Service]:
        """选择服务实例"""
        if not services:
            return None

        # 过滤健康的服务
        healthy_services = [s for s in services if s.status == "healthy"]

        if not healthy_services:
            return None

        if self.strategy == "round_robin":
            return self._round_robin(healthy_services)
        elif self.strategy == "random":
            return self._random(healthy_services)
        elif self.strategy == "weighted":
            return self._weighted(healthy_services)
        else:
            return healthy_services[0]

    def _round_robin(self, services: List[Service]) -> Service:
        """轮询算法"""
        service = services[self.current_index % len(services)]
        self.current_index += 1
        return service

    def _random(self, services: List[Service]) -> Service:
        """随机算法"""
        import random
        return random.choice(services)

    def _weighted(self, services: List[Service]) -> Service:
        """加权算法"""
        import random

        # 计算总权重
        total_weight = sum(s.weight for s in services)

        # 随机选择
        rand = random.uniform(0, total_weight)
        current = 0

        for service in services:
            current += service.weight
            if rand <= current:
                return service

        return services[-1]


class MetricsCollector:
    """指标收集器"""

    def __init__(self):
        self.requests: Dict[str, int] = defaultdict(int)
        self.errors: Dict[str, int] = defaultdict(int)
        self.latency: Dict[str, List[float]] = defaultdict(list)
        self.status_codes: Dict[str, Dict[int, int]] = defaultdict(lambda: defaultdict(int))

    def record_request(self, route: str, status_code: int, latency: float):
        """记录请求"""
        key = f"{route}"
        self.requests[key] += 1

        if status_code >= 400:
            self.errors[key] += 1

        self.latency[key].append(latency)

        # 保持最近1000条记录
        if len(self.latency[key]) > 1000:
            self.latency[key] = self.latency[key][-1000:]

        self.status_codes[key][status_code] += 1

    def get_metrics(self, route: str = None) -> Dict[str, Any]:
        """获取指标"""
        if route:
            key = route
            metrics = {
                "requests": self.requests.get(key, 0),
                "errors": self.errors.get(key, 0),
                "avg_latency": 0,
                "p95_latency": 0,
                "p99_latency": 0,
                "status_codes": dict(self.status_codes.get(key, {}))
            }

            if self.latency[key]:
                latencies = sorted(self.latency[key])
                metrics["avg_latency"] = sum(latencies) / len(latencies)
                metrics["p95_latency"] = latencies[int(len(latencies) * 0.95)]
                metrics["p99_latency"] = latencies[int(len(latencies) * 0.99)]

            return metrics

        return {
            "total_requests": sum(self.requests.values()),
            "total_errors": sum(self.errors.values()),
            "routes": len(self.requests)
        }

    def reset(self):
        """重置指标"""
        self.requests.clear()
        self.errors.clear()
        self.latency.clear()
        self.status_codes.clear()


class APIGateway:
    """API网关"""

    def __init__(self):
        self.routes: List[Route] = []
        self.services: Dict[str, List[Service]] = defaultdict(list)
        self.rate_limiters: Dict[str, RateLimiter] = {}  # 每个路由独立的限流器
        self.auth_manager = AuthManager()
        self.load_balancer = LoadBalancer(strategy="round_robin")
        self.metrics = MetricsCollector()

        # 中间件
        self.middleware: List[Callable] = []

        def add_middleware(self, middleware: Callable):
            """添加中间件"""
            self.middleware.append(middleware)

    def add_route(self, route: Route):
        """添加路由"""
        self.routes.append(route)

    def add_service(self, service: Service):
        """添加服务"""
        self.services[service.name].append(service)

    def find_route(self, path: str, method: str) -> Optional[Route]:
        """查找匹配的路由"""
        for route in self.routes:
            if route.enabled and route.match(path, method):
                return route
        return None

    def _execute_middleware(self, request: APIRequest) -> bool:
        """执行中间件"""
        for middleware in self.middleware:
            if not middleware(request):
                return False
        return True

    def _check_rate_limit(self, route: Route, client_id: str) -> bool:
        """检查限流"""
        key = f"{route.path}"
        
        # 为每个路由创建独立的限流器
        if key not in self.rate_limiters:
            self.rate_limiters[key] = RateLimiter(rate=route.rate_limit, per=60)
        
        limiter = self.rate_limiters[key]
        return limiter.check(client_id, 1)

    def _check_auth(self, route: Route, request: APIRequest) -> bool:
        """检查认证"""
        if not route.auth_required:
            return True

        # 检查API密钥
        api_key = request.headers.get("X-API-Key")
        if api_key and self.auth_manager.validate_api_key(api_key):
            return True

        # 检查JWT令牌
        auth_header = request.headers.get("Authorization")
        if auth_header:
            result = self.auth_manager.validate_token(auth_header)
            if result.get("valid"):
                return True

        return False

    def _forward_request(self, route: Route, request: APIRequest) -> APIResponse:
        """转发请求到目标服务（模拟）"""
        start_time = time.time()

        # 选择服务实例
        service_list = self.services.get(route.service_name, [])
        service = self.load_balancer.select(service_list)

        if not service:
            return APIResponse(
                request_id=request.id,
                status_code=503,
                body={"error": "Service unavailable"},
                service=route.service_name
            )

        # 模拟请求转发
        # 实际实现应该使用requests或aiohttp
        duration = time.time() - start_time

        response = APIResponse(
            request_id=request.id,
            status_code=200,
            body={"message": "OK", "service": service.name},
            duration=duration,
            service=route.service_name
        )

        return response

    def handle_request(self, request: APIRequest, client_id: str = "anonymous") -> APIResponse:
        """处理API请求"""
        start_time = time.time()

        # 执行中间件
        if not self._execute_middleware(request):
            return APIResponse(
                request_id=request.id,
                status_code=403,
                body={"error": "Forbidden by middleware"}
            )

        # 查找路由
        route = self.find_route(request.path, request.method)
        if not route:
            return APIResponse(
                request_id=request.id,
                status_code=404,
                body={"error": "Route not found"}
            )

        # 检查限流
        if not self._check_rate_limit(route, client_id):
            return APIResponse(
                request_id=request.id,
                status_code=429,
                body={"error": "Rate limit exceeded"}
            )

        # 检查认证
        if not self._check_auth(route, request):
            return APIResponse(
                request_id=request.id,
                status_code=401,
                body={"error": "Unauthorized"}
            )

        # 转发请求
        response = self._forward_request(route, request)

        # 记录指标
        duration = time.time() - start_time
        self.metrics.record_request(route.path, response.status_code, duration)

        return response

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        now = time.time()

        services_status = {}

        for service_name, service_list in self.services.items():
            healthy_count = sum(1 for s in service_list if s.status == "healthy")
            services_status[service_name] = {
                "total": len(service_list),
                "healthy": healthy_count,
                "unhealthy": len(service_list) - healthy_count
            }

        return {
            "status": "healthy",
            "timestamp": now,
            "services": services_status,
            "routes": len(self.routes)
        }

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        metrics = self.metrics.get_metrics()

        return {
            "gateway": {
                "routes": len(self.routes),
                "services": len(self.services)
            },
            "metrics": metrics
        }


# 辅助函数
def create_cors_middleware(allowed_origins: List[str] = ["*"]) -> Callable:
    """创建CORS中间件"""
    def middleware(request: APIRequest) -> bool:
        origin = request.headers.get("Origin", "")
        allowed = "*" in allowed_origins or origin in allowed_origins

        if not allowed:
            return False

        return True

    return middleware


def create_logging_middleware(log_path: str = "api_gateway.log") -> Callable:
    """创建日志中间件"""
    def middleware(request: APIRequest) -> bool:
        log_entry = {
            "timestamp": time.time(),
            "method": request.method,
            "path": request.path,
            "request_id": request.id
        }

        # 实际实现应该写入文件
        # 这里简化处理
        return True

    return middleware


def create_cache_middleware(cache_duration: int = 60) -> Callable:
    """创建缓存中间件（简化版）"""
    cache = {}

    def middleware(request: APIRequest) -> bool:
        if request.method != "GET":
            return True

        cache_key = f"{request.method}:{request.path}"

        # 检查缓存
        if cache_key in cache:
            entry = cache[cache_key]
            if time.time() - entry["timestamp"] < cache_duration:
                return True

        return True

    return middleware
