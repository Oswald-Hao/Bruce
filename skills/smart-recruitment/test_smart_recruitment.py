#!/usr/bin/env python3
"""
智能招聘系统测试
测试所有核心功能
"""

import json
import os
import sys
import tempfile
from pathlib import Path

# 添加父目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smart_recruitment import (
    ResumeParser,
    CandidateManager
)


class TestResumeParser:
    """简历解析器测试"""

    def __init__(self):
        self.passed = 0
        self.failed = 0

    def assert_equal(self, actual, expected, test_name):
        if actual == expected:
            self.passed += 1
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            print(f"  ✗ {test_name}: expected {expected}, got {actual}")

    def assert_not_none(self, value, test_name):
        if value is not None:
            self.passed += 1
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            print(f"  ✗ {test_name}: value is None")

    def assert_greater(self, actual, min_val, test_name):
        if actual > min_val:
            self.passed += 1
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            print(f"  ✗ {test_name}: expected > {min_val}, got {actual}")

    def assert_in(self, item, container, test_name):
        if item in container:
            self.passed += 1
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            print(f"  ✗ {test_name}: {item} not in {container}")

    def test_parse_text_resume(self):
        """测试文本简历解析"""
        print("\n[测试] 简历解析器 - 文本简历")

        # 创建临时简历文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("张三\n")
            f.write("邮箱: zhangsan@example.com\n")
            f.write("电话: 13800138000\n")
            f.write("工作经验: 5年\n")
            f.write("学历: 本科\n")
            f.write("技能: Python, Java, JavaScript, React, Docker, Git\n")
            resume_path = f.name

        try:
            result = ResumeParser.parse(resume_path)

            self.assert_not_none(result, "解析结果非空")
            self.assert_equal(result['name'], '张三', "姓名提取")
            self.assert_equal(result['email'], 'zhangsan@example.com', "邮箱提取")
            self.assert_equal(result['phone'], '13800138000', "电话提取")
            self.assert_equal(result['experience'], 5, "工作年限提取")
            self.assert_in('本科', result['education'], "学历提取")
            self.assert_in('Python', result['skills'], "技能提取")
            self.assert_in('Java', result['skills'], "技能提取")

        finally:
            os.unlink(resume_path)

    def test_extract_email(self):
        """测试邮箱提取"""
        print("\n[测试] 简历解析器 - 邮箱提取")

        text = "联系方式: zhangsan@example.com 或 john.doe@test.com"
        email = ResumeParser._extract_email(text)
        self.assert_equal(email, 'zhangsan@example.com', "邮箱提取")

    def test_extract_phone(self):
        """测试电话提取"""
        print("\n[测试] 简历解析器 - 电话提取")

        text = "手机: 13800138000 或 13900139000"
        phone = ResumeParser._extract_phone(text)
        self.assert_equal(phone, '13800138000', "电话提取")

    def test_extract_experience(self):
        """测试工作经验提取"""
        print("\n[测试] 简历解析器 - 工作经验提取")

        # 测试中文格式
        text1 = "工作经验: 3年"
        exp1 = ResumeParser._extract_experience(text1)
        self.assert_equal(exp1, 3, "中文工作经验提取")

        # 测试英文格式
        text2 = "5 years of experience"
        exp2 = ResumeParser._extract_experience(text2)
        self.assert_equal(exp2, 5, "英文工作经验提取")

    def run_all(self):
        """运行所有测试"""
        print("=" * 60)
        print("简历解析器测试")
        print("=" * 60)

        self.test_parse_text_resume()
        self.test_extract_email()
        self.test_extract_phone()
        self.test_extract_experience()

        print(f"\n结果: {self.passed} 通过, {self.failed} 失败")
        return self.failed == 0


class TestCandidateManager:
    """候选人管理器测试"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.temp_dir = tempfile.mkdtemp()

    def assert_equal(self, actual, expected, test_name):
        if actual == expected:
            self.passed += 1
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            print(f"  ✗ {test_name}: expected {expected}, got {actual}")

    def assert_not_none(self, value, test_name):
        if value is not None:
            self.passed += 1
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            print(f"  ✗ {test_name}: value is None")

    def assert_greater(self, actual, min_val, test_name):
        if actual > min_val:
            self.passed += 1
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            print(f"  ✗ {test_name}: expected > {min_val}, got {actual}")

    def assert_true(self, value, test_name):
        if value:
            self.passed += 1
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            print(f"  ✗ {test_name}: expected True, got {value}")

    def assert_in(self, item, container, test_name):
        if item in container:
            self.passed += 1
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            print(f"  ✗ {test_name}: {item} not in {container}")

    def test_add_candidate(self):
        """测试添加候选人"""
        print("\n[测试] 候选人管理 - 添加候选人")

        # 创建临时简历文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("李四\n")
            f.write("邮箱: lisi@example.com\n")
            f.write("电话: 13900139000\n")
            f.write("工作经验: 3年\n")
            f.write("技能: Python, Django, MySQL, Redis\n")
            resume_path = f.name

        try:
            manager = CandidateManager(self.temp_dir)
            candidate = manager.add_candidate(
                name="李四",
                resume_path=resume_path,
                position="后端开发工程师",
                tags=["Python", "3年经验"]
            )

            self.assert_not_none(candidate, "候选人创建成功")
            self.assert_equal(candidate['id'], 1, "候选人ID")
            self.assert_equal(candidate['name'], '李四', "候选人姓名")
            self.assert_equal(candidate['position'], '后端开发工程师', "候选人职位")
            self.assert_equal(candidate['status'], 'pending', "候选人状态")
            self.assert_in('Python', candidate['tags'], "标签设置")

        finally:
            os.unlink(resume_path)

    def test_get_candidate(self):
        """测试获取候选人"""
        print("\n[测试] 候选人管理 - 获取候选人")

        manager = CandidateManager(self.temp_dir)
        candidate = manager.get_candidate(1)

        self.assert_not_none(candidate, "获取候选人成功")
        self.assert_equal(candidate['name'], '李四', "候选人姓名正确")

    def test_update_candidate(self):
        """测试更新候选人"""
        print("\n[测试] 候选人管理 - 更新候选人")

        manager = CandidateManager(self.temp_dir)
        success = manager.update_candidate(1, status='interviewing')

        self.assert_true(success, "更新候选人成功")

        candidate = manager.get_candidate(1)
        self.assert_equal(candidate['status'], 'interviewing', "状态更新正确")

    def test_search_candidates(self):
        """测试搜索候选人"""
        print("\n[测试] 候选人管理 - 搜索候选人")

        manager = CandidateManager(self.temp_dir)

        # 添加更多候选人
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("王五\n")
            f.write("工作经验: 5年\n")
            f.write("技能: Java, Spring, MySQL\n")
            resume_path = f.name

        manager.add_candidate("王五", resume_path, "Java工程师", ["Java"])
        os.unlink(resume_path)

        # 搜索测试
        results = manager.search_candidates(keyword="Python")
        self.assert_greater(len(results), 0, "关键词搜索")

        results = manager.search_candidates(min_experience=3)
        self.assert_greater(len(results), 0, "经验筛选")

        results = manager.search_candidates(required_skills=["Python"])
        self.assert_greater(len(results), 0, "技能筛选")

    def test_rate_candidate(self):
        """测试面试评分"""
        print("\n[测试] 候选人管理 - 面试评分")

        manager = CandidateManager(self.temp_dir)
        success = manager.rate_candidate(
            candidate_id=1,
            round_name="技术面",
            score=85,
            feedback="技术基础扎实",
            interviewer="张工"
        )

        self.assert_true(success, "评分成功")

        interviews = manager.get_candidate_interviews(1)
        self.assert_greater(len(interviews), 0, "面试记录存在")
        self.assert_equal(interviews[0]['score'], 85, "分数正确")
        self.assert_equal(interviews[0]['round'], "技术面", "面试轮次")

    def test_schedule_interview(self):
        """测试安排面试"""
        print("\n[测试] 候选人管理 - 安排面试")

        manager = CandidateManager(self.temp_dir)
        success = manager.schedule_interview(
            candidate_id=1,
            datetime_str="2026-02-20 14:00",
            round_name="HR面",
            interviewer="HR"
        )

        self.assert_true(success, "安排面试成功")

        interviews = manager.get_candidate_interviews(1)
        self.assert_greater(len(interviews), 1, "面试记录增加")
        scheduled = [i for i in interviews if i.get('scheduled_time')]
        self.assert_greater(len(scheduled), 0, "定时面试存在")

    def test_calculate_score(self):
        """测试计算匹配分数"""
        print("\n[测试] 候选人管理 - 计算匹配分数")

        manager = CandidateManager(self.temp_dir)
        candidate = manager.get_candidate(1)

        requirements = {
            'min_experience': 2,
            'required_skills': ['Python'],
            'education_level': '大专',
            'keywords': []
        }

        score = manager.calculate_score(candidate, requirements)
        self.assert_greater(score, 70, "匹配分数合理")

    def test_rank_candidates(self):
        """测试候选人排名"""
        print("\n[测试] 候选人管理 - 候选人排名")

        manager = CandidateManager(self.temp_dir)
        requirements = {
            'min_experience': 3,
            'required_skills': ['Python'],
            'keywords': []
        }

        ranked = manager.rank_candidates(requirements)
        self.assert_greater(len(ranked), 0, "排名结果存在")

        # 验证排序
        for i in range(len(ranked) - 1):
            self.assert_true(
                ranked[i][1] >= ranked[i+1][1],
                f"排序正确 (位置 {i})"
            )

    def test_get_stats(self):
        """测试统计数据"""
        print("\n[测试] 候选人管理 - 统计数据")

        manager = CandidateManager(self.temp_dir)
        stats = manager.get_stats()

        self.assert_greater(stats['total_candidates'], 0, "总候选人数")
        self.assert_true('by_status' in stats, "状态统计存在")
        self.assert_true('by_position' in stats, "职位统计存在")

    def test_export_data(self):
        """测试导出数据"""
        print("\n[测试] 候选人管理 - 导出数据")

        manager = CandidateManager(self.temp_dir)
        path = manager.export_data(format='json')

        self.assert_true(os.path.exists(path), "导出文件存在")

        # 验证数据
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assert_true('candidates' in data, "候选人数据存在")
            self.assert_true('interviews' in data, "面试数据存在")

        os.unlink(path)

    def run_all(self):
        """运行所有测试"""
        print("=" * 60)
        print("候选人管理器测试")
        print("=" * 60)

        self.test_add_candidate()
        self.test_get_candidate()
        self.test_update_candidate()
        self.test_search_candidates()
        self.test_rate_candidate()
        self.test_schedule_interview()
        self.test_calculate_score()
        self.test_rank_candidates()
        self.test_get_stats()
        self.test_export_data()

        print(f"\n结果: {self.passed} 通过, {self.failed} 失败")
        return self.failed == 0


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("智能招聘系统 - 完整测试套件")
    print("=" * 60)

    all_passed = True

    # 运行简历解析器测试
    resume_parser_tests = TestResumeParser()
    if not resume_parser_tests.run_all():
        all_passed = False

    # 运行候选人管理器测试
    candidate_manager_tests = TestCandidateManager()
    if not candidate_manager_tests.run_all():
        all_passed = False

    # 清理临时目录
    import shutil
    shutil.rmtree(candidate_manager_tests.temp_dir, ignore_errors=True)

    # 总结
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有测试通过！")
        print("=" * 60)
        return 0
    else:
        print("❌ 部分测试失败")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
