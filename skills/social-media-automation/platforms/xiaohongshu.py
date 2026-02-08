"""
小红书平台适配器
"""

from .base import BasePlatform
from typing import Dict, List, Any


class XiaohongshuPlatform(BasePlatform):
    """小红书平台适配器"""

    def _init_client(self):
        """初始化小红书客户端（模拟）"""
        print(f"📱 初始化小红书平台...")
        return {
            'client_id': self.config.get('client_id', ''),
            'access_token': self.config.get('access_token', '')
        }

    def publish(
        self,
        content: str,
        media_files: List[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """发布内容到小红书"""
        try:
            if not self.validate_content(content):
                return self._format_error("内容无效或超长")

            post_id = f"xhs_{self._generate_post_id()}"
            self._mock_publish_api(content, media_files, kwargs)

            return self._format_success(
                post_id=post_id,
                url=f"https://www.xiaohongshu.com/explore/{post_id}",
                views=0,
                likes=0,
                collects=0
            )

        except Exception as e:
            return self._format_error(f"发布失败: {str(e)}")

    def get_post_stats(self, post_id: str) -> Dict[str, Any]:
        """获取小红书帖子统计"""
        return {
            'views': 2341,
            'likes': 567,
            'collects': 234,
            'comments': 89,
            'post_id': post_id
        }

    def get_account_info(self) -> Dict[str, Any]:
        """获取小红书账号信息"""
        return {
            'username': self.config.get('username', ''),
            'fans': 23400,
            'following': 456,
            'posts': 789
        }

    def _get_max_content_length(self) -> int:
        """小红书文案最大长度"""
        return 3000

    def _generate_post_id(self) -> str:
        """生成模拟帖子ID"""
        import random
        import string
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))

    def _mock_publish_api(self, content: str, media_files: List[str], kwargs: Dict) -> Dict:
        """模拟发布API调用"""
        print(f"  📝 内容: {content[:50]}...")
        print(f"  🖼️  媒体文件: {len(media_files) if media_files else 0}个")
        print(f"  🏷️  标题: {kwargs.get('title', '')}")

        return {'status': 'success'}
