#!/usr/bin/env python3
"""
API网关和微服务管理系统测试
"""

import sys
import os
import time
import json

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api_gateway import (
    Route, Service, APIRequest, APIResponse,
    RateLimiter, AuthManager, LoadBalancer,
    MetricsCollector, APIGateway,
    create_cors_middleware, create_logging_middleware,
    create_cache_middleware
)


def test_route():
    """测试路由"""
    print("测试 1: Route")

    route = Route(
        path="/api/users",
        method="GET",
        target_url="http://users-service",
        service_name="users"
    )

    assert route.path == "/api/users"
    assert route.method == "GET"

    # 测试匹配
    assert route.match("/api/users", "GET")
    assert not route.match("/api/users", "POST")
    assert not route.match("/api/products", "GET")

    # 测试通配符
    wildcard_route = Route(
        path="*",
        method="*",
        target_url="http://default-service",
        service_name="default"
    )

    assert wildcard_route.match("/any/path", "POST")

    print("  ✓ 路由创建成功")
    print("  ✓ 路由匹配成功")
    print("  ✓ 通配符匹配成功")
    print("  测试通过!\n")


def test_rate_limiter():
    """测试限流器"""
    print("测试 2: RateLimiter")

    limiter = RateLimiter(rate=10, per=60)

    # 测试正常请求
    for i in range(10):
        assert limiter.check("client_1")

    # 测试超出限流
    assert not limiter.check("client_1")

    # 测试不同客户端
    assert limiter.check("client_2")

    # 测试重置
    limiter.reset("client_1")
    assert limiter.check("client_1")

    print("  ✓ 限流检查成功")
    print("  ✓ 超出限流成功")
    print("  ✓ 不同客户端隔离成功")
    print("  ✓ 重置功能成功")
    print("  测试通过!\n")


def test_auth_manager():
    """测试认证管理器"""
    print("测试 3: AuthManager")

    auth = AuthManager()

    # 测试生成API密钥
    api_key = auth.generate_api_key("client_1", ["read", "write"])

    assert api_key.startswith("sk_")
    assert auth.validate_api_key(api_key)

    # 测试无效密钥
    assert not auth.validate_api_key("invalid_key")

    # 测试JWT验证（简化版）
    result = auth.validate_token("Bearer valid_token")
    assert result.get("valid") is True

    result = auth.validate_token("Invalid")
    assert result.get("valid") is False

    # 测试权限检查
    assert auth.check_scope(api_key, "read")
    assert auth.check_scope(api_key, "write")
    assert not auth.check_scope(api_key, "delete")

    print("  ✓ API密钥生成成功")
    print("  ✓ API密钥验证成功")
    print("  ✓ JWT令牌验证成功")
    print("  ✓ 权限检查成功")
    print("  测试通过!\n")


def test_load_balancer():
    """测试负载均衡器"""
    print("测试 4: LoadBalancer")

    services = [
        Service("service1", "http://service1", weight=100),
        Service("service2", "http://service2", weight=200),
        Service("service3", "http://service3", weight=300),
    ]

    # 测试轮询
    lb_round = LoadBalancer(strategy="round_robin")
    selected = [lb_round.select(services) for _ in range(6)]

    # 应该轮询选择
    assert len(selected) == 6
    assert selected[0].name != selected[1].name

    # 测试随机
    lb_random = LoadBalancer(strategy="random")
    service = lb_random.select(services)
    assert service in services

    # 测试加权
    lb_weighted = LoadBalancer(strategy="weighted")
    weighted_selected = [lb_weighted.select(services) for _ in range(100)]

    # service3的权重最高，应该被选中最多次
    counts = {}
    for s in weighted_selected:
        counts[s.name] = counts.get(s.name, 0) + 1

    assert counts["service3"] > counts["service1"]

    print("  ✓ 轮询策略成功")
    print("  ✓ 随机策略成功")
    print("  ✓ 加权策略成功")
    print("  测试通过!\n")


def test_metrics_collector():
    """测试指标收集器"""
    print("测试 5: MetricsCollector")

    collector = MetricsCollector()

    # 记录一些请求
    collector.record_request("/api/users", 200, 0.1)
    collector.record_request("/api/users", 200, 0.2)
    collector.record_request("/api/users", 404, 0.3)
    collector.record_request("/api/products", 200, 0.4)

    # 获取特定路由的指标
    metrics = collector.get_metrics("/api/users")

    assert metrics["requests"] == 3
    assert metrics["errors"] == 1
    assert metrics["avg_latency"] > 0
    assert 200 in metrics["status_codes"]
    assert 404 in metrics["status_codes"]

    # 获取全局指标
    global_metrics = collector.get_metrics()
    assert global_metrics["total_requests"] == 4
    assert global_metrics["total_errors"] == 1
    assert global_metrics["routes"] == 2

    # 测试重置
    collector.reset()
    metrics_after = collector.get_metrics()
    assert metrics_after["total_requests"] == 0

    print("  ✓ 记录请求成功")
    print("  ✓ 获取路由指标成功")
    print("  ✓ 获取全局指标成功")
    print("  ✓ 重置指标成功")
    print("  测试通过!\n")


def test_api_gateway():
    """测试API网关"""
    print("测试 6: APIGateway")

    gateway = APIGateway()

    # 添加路由
    route1 = Route(
        path="/api/users",
        method="GET",
        target_url="http://users-service",
        service_name="users"
    )

    route2 = Route(
        path="/api/products",
        method="GET",
        target_url="http://products-service",
        service_name="products",
        auth_required=True
    )

    gateway.add_route(route1)
    gateway.add_route(route2)

    # 添加服务
    service1 = Service("users", "http://users:8001")
    service2 = Service("products", "http://products:8001")

    gateway.add_service(service1)
    gateway.add_service(service2)

    # 测试请求处理
    request = APIRequest(path="/api/users", method="GET")
    response = gateway.handle_request(request, "client_1")

    assert response.status_code == 200
    assert response.service == "users"

    # 测试未找到路由
    request_404 = APIRequest(path="/api/unknown", method="GET")
    response_404 = gateway.handle_request(request_404, "client_1")

    assert response_404.status_code == 404

    # 测试认证失败
    request_auth = APIRequest(path="/api/products", method="GET")
    response_auth = gateway.handle_request(request_auth, "client_1")

    assert response_auth.status_code == 401

    print("  ✓ 路由添加成功")
    print("  ✓ 服务添加成功")
    print("  ✓ 请求处理成功")
    print("  ✓ 404错误正确返回")
    print("  ✓ 认证检查成功")
    print("  测试通过!\n")


def test_middleware():
    """测试中间件"""
    print("测试 7: Middleware")

    gateway = APIGateway()

    # 添加CORS中间件
    cors_middleware = create_cors_middleware(["http://localhost:3000"])
    gateway.add_middleware = cors_middleware

    # 添加路由
    route = Route(
        path="/api/test",
        method="GET",
        target_url="http://test-service",
        service_name="test"
    )
    gateway.add_route(route)
    gateway.add_service(Service("test", "http://test:8001"))

    # 测试请求
    request = APIRequest(path="/api/test", method="GET")
    response = gateway.handle_request(request, "client_1")

    assert response.status_code == 200

    print("  ✓ CORS中间件创建成功")
    print("  ✓ 中间件执行成功")
    print("  测试通过!\n")


def test_service_health_check():
    """测试服务健康检查"""
    print("测试 8: Service Health Check")

    gateway = APIGateway()

    # 添加多个服务实例
    service1 = Service("users", "http://users1:8001")
    service2 = Service("users", "http://users2:8001")
    service3 = Service("products", "http://products:8001")

    service2.status = "unhealthy"

    gateway.add_service(service1)
    gateway.add_service(service2)
    gateway.add_service(service3)

    # 健康检查
    health = gateway.health_check()

    assert health["status"] == "healthy"
    assert "users" in health["services"]
    assert health["services"]["users"]["total"] == 2
    assert health["services"]["users"]["healthy"] == 1
    assert health["services"]["users"]["unhealthy"] == 1

    print("  ✓ 健康检查成功")
    print("  ✓ 服务状态统计正确")
    print("  测试通过!\n")


def test_gateway_statistics():
    """测试网关统计"""
    print("测试 9: Gateway Statistics")

    gateway = APIGateway()

    # 添加路由和服务
    route = Route(
        path="/api/test",
        method="GET",
        target_url="http://test-service",
        service_name="test"
    )

    gateway.add_route(route)
    gateway.add_service(Service("test", "http://test:8001"))

    # 发送多个请求
    for i in range(10):
        request = APIRequest(path="/api/test", method="GET")
        gateway.handle_request(request, "client_1")

    # 获取统计
    stats = gateway.get_stats()

    assert stats["gateway"]["routes"] == 1
    assert stats["gateway"]["services"] == 1
    assert stats["metrics"]["total_requests"] == 10

    print("  ✓ 统计信息获取成功")
    print("  ✓ 请求数量统计正确")
    print("  测试通过!\n")


def test_complex_workflow():
    """测试复杂工作流"""
    print("测试 10: Complex Workflow")

    gateway = APIGateway()

    # 添加多个路由
    routes = [
        Route("/api/users", "GET", "http://users-service", "users"),
        Route("/api/products", "GET", "http://products-service", "products"),
        Route("/api/orders", "GET", "http://orders-service", "orders"),
    ]

    for route in routes:
        gateway.add_route(route)

    # 添加多个服务实例
    services = [
        Service("users", "http://users1:8001", weight=100),
        Service("users", "http://users2:8001", weight=200),
        Service("products", "http://products1:8001"),
        Service("orders", "http://orders1:8001"),
    ]

    for service in services:
        gateway.add_service(service)

    # 生成多个客户端请求
    clients = ["client_1", "client_2", "client_3"]

    responses = []
    for client in clients:
        for route in routes:
            request = APIRequest(path=route.path, method=route.method)
            response = gateway.handle_request(request, client)
            responses.append(response)

    # 验证所有请求都成功
    successful = [r for r in responses if r.status_code == 200]
    assert len(successful) == len(responses)

    # 检查统计
    stats = gateway.get_stats()
    assert stats["metrics"]["total_requests"] == len(responses)

    # 检查健康状态
    health = gateway.health_check()
    assert health["status"] == "healthy"
    assert len(health["services"]) == 3

    print("  ✓ 多路由配置成功")
    print("  ✓ 多服务实例配置成功")
    print("  ✓ 多客户端请求处理成功")
    print("  ✓ 统计信息正确")
    print("  ✓ 健康检查正常")
    print("  测试通过!\n")


def test_serialization():
    """测试序列化"""
    print("测试 11: Serialization")

    from dataclasses import asdict

    route = Route(
        path="/api/test",
        method="GET",
        target_url="http://test-service",
        service_name="test"
    )

    # 转换为字典
    route_dict = asdict(route)

    assert route_dict["path"] == "/api/test"
    assert route_dict["method"] == "GET"
    assert route_dict["service_name"] == "test"

    # 序列化为JSON
    json_str = json.dumps(route_dict, ensure_ascii=False)

    assert "/api/test" in json_str

    print("  ✓ 路由序列化成功")
    print("  ✓ JSON序列化成功")
    print("  测试通过!\n")


def test_rate_limit_with_burst():
    """测试突发限流"""
    print("测试 12: Rate Limit with Burst")

    gateway = APIGateway()

    # 添加路由（限制每分钟5个请求）
    route = Route(
        path="/api/test",
        method="GET",
        target_url="http://test-service",
        service_name="test",
        rate_limit=5
    )

    gateway.add_route(route)
    gateway.add_service(Service("test", "http://test:8001"))

    # 发送10个请求
    success_count = 0
    error_count = 0

    for i in range(10):
        request = APIRequest(path="/api/test", method="GET")
        response = gateway.handle_request(request, "client_1")

        if response.status_code == 200:
            success_count += 1
        elif response.status_code == 429:
            error_count += 1

    # 前5个应该成功，后5个应该被限流
    assert success_count <= 5
    assert error_count >= 5

    print("  ✓ 突发流量限流成功")
    print(f"  ✓ 成功请求: {success_count}, 限流请求: {error_count}")
    print("  测试通过!\n")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("API网关和微服务管理系统 - 测试套件")
    print("=" * 60)
    print()

    tests = [
        test_route,
        test_rate_limiter,
        test_auth_manager,
        test_load_balancer,
        test_metrics_collector,
        test_api_gateway,
        test_middleware,
        test_service_health_check,
        test_gateway_statistics,
        test_complex_workflow,
        test_serialization,
        test_rate_limit_with_burst
    ]

    passed = 0
    failed = 0

    start_time = time.time()

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"  ✗ 测试失败: {e}\n")

    end_time = time.time()
    duration = end_time - start_time

    print("=" * 60)
    print(f"测试总结: {passed} 通过, {failed} 失败")
    print(f"用时: {duration:.2f} 秒")
    print(f"通过率: {passed/(passed+failed)*100:.1f}%")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
