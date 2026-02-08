"""
平台基类 - 定义所有平台的通用接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any


class BasePlatform(ABC):
    """平台适配器基类"""

    def __init__(self, config: Dict[str, Any]):
        """初始化平台"""
        self.config = config
        self.platform_name = self.__class__.__name__.replace('Platform', '').lower()
        self.client = self._init_client()

    @abstractmethod
    def _init_client(self):
        """初始化平台客户端"""
        pass

    @abstractmethod
    def publish(
        self,
        content: str,
        media_files: List[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发布内容

        Args:
            content: 内容文本
            media_files: 媒体文件列表
            **kwargs: 其他参数

        Returns:
            包含发布结果的字典
        """
        pass

    @abstractmethod
    def get_post_stats(self, post_id: str) -> Dict[str, Any]:
        """获取帖子统计数据"""
        pass

    @abstractmethod
    def get_account_info(self) -> Dict[str, Any]:
        """获取账号信息"""
        pass

    def validate_content(self, content: str) -> bool:
        """验证内容是否合规"""
        if not content or len(content.strip()) == 0:
            return False

        # 检查内容长度
        max_length = self._get_max_content_length()
        if len(content) > max_length:
            return False

        return True

    def _get_max_content_length(self) -> int:
        """获取最大内容长度"""
        return 5000

    def _format_error(self, message: str) -> Dict[str, Any]:
        """格式化错误信息"""
        return {
            'success': False,
            'error': message,
            'platform': self.platform_name
        }

    def _format_success(self, post_id: str = None, **kwargs) -> Dict[str, Any]:
        """格式化成功信息"""
        result = {
            'success': True,
            'platform': self.platform_name,
            'post_id': post_id,
            'timestamp': self._get_timestamp()
        }
        result.update(kwargs)
        return result

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
