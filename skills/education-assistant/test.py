#!/usr/bin/env python3
"""
测试教育辅助系统
"""

import tempfile
import json
from pathlib import Path

import sys
# 直接导入当前目录的skill模块
skill_path = str(Path(__file__).parent)
sys.path.insert(0, skill_path)

from skill import EducationAssistant, Question, StudyPlan, TestResult


def test_generate_study_plan():
    """测试生成学习计划"""
    print("测试1: 生成学习计划...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            assistant = EducationAssistant({'data_dir': temp_dir})
            
            plan = assistant.generate_study_plan(
                subject='编程',
                topics=['Python基础', '算法'],
                difficulty='medium',
                total_hours=10
            )
            
            assert plan.subject == '编程', "学科不正确"
            assert 'Python基础' in plan.topic, "主题不正确"
            assert plan.duration == 600, "时长不正确"
            assert len(plan.tasks) >= 4, "任务数不正确"
            assert len(plan.resources) > 0, "推荐资源为空"
        
        print("✓ 生成学习计划成功")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def test_add_question():
    """测试添加题目"""
    print("\n测试2: 添加题目...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            assistant = EducationAssistant({'data_dir': temp_dir})
            
            qid = assistant.add_question(
                question="Python中print()的作用是什么？",
                options=["输出数据", "输入数据", "计算数据", "删除数据"],
                correct_answer="输出数据",
                explanation="print()函数用于在控制台输出信息",
                subject="编程",
                topic="Python基础",
                difficulty="easy"
            )
            
            assert qid.startswith('编程_'), "题目ID格式不正确"
            assert len(assistant.questions) == 1, "题目数量不正确"
            assert assistant.questions[0]['question'] == "Python中print()的作用是什么？", "题目内容不正确"
        
        print("✓ 添加题目成功")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def test_generate_test():
    """测试生成测试"""
    print("\n测试3: 生成测试...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            assistant = EducationAssistant({'data_dir': temp_dir})
            
            # 添加一些题目
            assistant.add_question(
                question="Q1", options=["A", "B", "C", "D"],
                correct_answer="A", explanation="E1",
                subject="数学", topic="代数", difficulty="easy"
            )
            assistant.add_question(
                question="Q2", options=["A", "B", "C", "D"],
                correct_answer="B", explanation="E2",
                subject="数学", topic="代数", difficulty="easy"
            )
            assistant.add_question(
                question="Q3", options=["A", "B", "C", "D"],
                correct_answer="C", explanation="E3",
                subject="数学", topic="几何", difficulty="medium"
            )
            
            # 生成测试
            test = assistant.generate_test(
                subject="数学",
                topic="代数",
                difficulty="easy",
                count=5
            )
            
            assert len(test) == 2, f"应该有2道题，实际{len(test)}道"
            assert all(q.subject == "数学" for q in test), "题目学科不正确"
            assert all(q.topic == "代数" for q in test), "题目主题不正确"
        
        print("✓ 生成测试成功")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def test_submit_test():
    """测试提交测试"""
    print("\n测试4: 提交测试...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            assistant = EducationAssistant({'data_dir': temp_dir})
            
            # 添加题目
            assistant.add_question(
                question="1+1=?", options=["1", "2", "3", "4"],
                correct_answer="2", explanation="1+1=2",
                subject="数学", topic="基础", difficulty="easy"
            )
            assistant.add_question(
                question="2+2=?", options=["1", "2", "3", "4"],
                correct_answer="4", explanation="2+2=4",
                subject="数学", topic="基础", difficulty="easy"
            )
            
            # 生成测试
            test = assistant.generate_test(subject="数学", difficulty="easy", count=2)
            
            # 调试：打印题目信息
            print(f"调试: test类型={type(test)}, 长度={len(test)}")
            for i, q in enumerate(test):
                print(f"调试: 题目{i+1} type={type(q)}, correct_answer={getattr(q, 'correct_answer', 'N/A')}")
            
            # 提交答案（1对1错）
            result = assistant.submit_test(test, ["2", "3"], time_spent=60)
            
            assert result.score == 50.0, f"分数不正确，期望50，实际{result.score}"
            assert result.correct == 1, "正确题数不正确"
            assert result.total == 2, "总题数不正确"
            assert len(result.wrong_questions) == 1, "错题数不正确"
        
        print("✓ 提交测试成功")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def test_get_study_progress():
    """测试获取学习进度"""
    print("\n测试5: 获取学习进度...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            assistant = EducationAssistant({'data_dir': temp_dir})
            
            # 添加题目
            assistant.add_question(
                question="Q1", options=["A", "B"], correct_answer="A",
                explanation="E1", subject="英语", topic="单词", difficulty="easy"
            )
            
            # 生成并提交测试
            test = assistant.generate_test(subject="英语", count=1)
            assistant.submit_test(test, ["A"], time_spent=30)
            
            # 获取进度
            progress = assistant.get_study_progress("英语")
            
            assert 'total_tests' in progress, "缺少total_tests"
            assert progress['total_tests'] == 1, "测试数不正确"
            assert 'average_score' in progress, "缺少average_score"
            assert progress['average_score'] == 100.0, "平均分不正确"
        
        print("✓ 获取学习进度成功")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def test_get_wrong_questions():
    """测试获取错题"""
    print("\n测试6: 获取错题...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            assistant = EducationAssistant({'data_dir': temp_dir})
            
            # 添加3道题
            assistant.add_question(
                question="Q1", options=["A", "B"], correct_answer="A",
                explanation="E1", subject="物理", topic="力学", difficulty="easy"
            )
            assistant.add_question(
                question="Q2", options=["A", "B"], correct_answer="B",
                explanation="E2", subject="物理", topic="力学", difficulty="easy"
            )
            assistant.add_question(
                question="Q3", options=["A", "B"], correct_answer="A",
                explanation="E3", subject="物理", topic="电学", difficulty="easy"
            )
            
            # 生成测试并提交（全部答错）
            test = assistant.generate_test(subject="物理", count=3)
            assistant.submit_test(test, ["B", "A", "B"], time_spent=90)
            
            # 获取错题
            wrong_questions = assistant.get_wrong_questions(subject="物理")
            
            assert len(wrong_questions) == 3, f"错题数不正确，期望3，实际{len(wrong_questions)}"
        
        print("✓ 获取错题成功")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def test_generate_review_plan():
    """测试生成复习计划"""
    print("\n测试7: 生成复习计划...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            assistant = EducationAssistant({'data_dir': temp_dir})
            
            # 添加题目
            assistant.add_question(
                question="Q1", options=["A", "B"], correct_answer="A",
                explanation="E1", subject="化学", topic="有机", difficulty="easy"
            )
            assistant.add_question(
                question="Q2", options=["A", "B"], correct_answer="A",
                explanation="E2", subject="化学", topic="无机", difficulty="easy"
            )
            
            # 答错
            test = assistant.generate_test(subject="化学", count=2)
            assistant.submit_test(test, ["B", "B"], time_spent=60)
            
            # 生成复习计划
            review_plan = assistant.generate_review_plan(subject="化学", days=3)
            
            assert review_plan['wrong_questions_count'] == 2, "错题数不正确"
            assert 'daily_tasks' in review_plan, "缺少daily_tasks"
            assert len(review_plan['daily_tasks']) == 3, "复习天数不正确"
        
        print("✓ 生成复习计划成功")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def test_get_learning_stats():
    """测试获取学习统计"""
    print("\n测试8: 获取学习统计...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            assistant = EducationAssistant({'data_dir': temp_dir})
            
            # 添加题目和生成测试
            assistant.add_question(
                question="Q1", options=["A", "B"], correct_answer="A",
                explanation="E1", subject="生物", topic="细胞", difficulty="easy"
            )
            test = assistant.generate_test(subject="生物", count=1)
            assistant.submit_test(test, ["A"], time_spent=30)
            
            # 获取统计
            stats = assistant.get_learning_stats()
            
            assert 'total_questions' in stats, "缺少total_questions"
            assert stats['total_questions'] == 1, "题目数不正确"
            assert 'total_tests' in stats, "缺少total_tests"
            assert stats['total_tests'] == 1, "测试数不正确"
            assert 'average_score' in stats, "缺少average_score"
            assert stats['average_score'] == 100.0, "平均分不正确"
        
        print("✓ 获取学习统计成功")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def test_create_reminder():
    """测试创建学习提醒"""
    print("\n测试9: 创建学习提醒...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            assistant = EducationAssistant({'data_dir': temp_dir})
            
            reminder = assistant.create_reminder(
                subject="历史",
                topic="近代史",
                time="20:00",
                message="该学习近代史了！"
            )
            
            assert reminder['subject'] == "历史", "学科不正确"
            assert reminder['topic'] == "近代史", "主题不正确"
            assert reminder['time'] == "20:00", "时间不正确"
            assert reminder['message'] == "该学习近代史了！", "消息不正确"
            assert 'created_at' in reminder, "缺少created_at"
        
        print("✓ 创建学习提醒成功")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def test_data_persistence():
    """测试数据持久化"""
    print("\n测试10: 数据持久化...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建第一个实例
            assistant1 = EducationAssistant({'data_dir': temp_dir})
            assistant1.add_question(
                question="测试题目", options=["A", "B"], correct_answer="A",
                explanation="测试", subject="测试", topic="测试", difficulty="easy"
            )
            
            # 创建第二个实例
            assistant2 = EducationAssistant({'data_dir': temp_dir})
            
            # 验证数据持久化
            assert len(assistant2.questions) == 1, "数据未持久化"
            assert assistant2.questions[0]['question'] == "测试题目", "数据内容不正确"
        
        print("✓ 数据持久化成功")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("教育辅助系统 - 功能测试")
    print("=" * 60)
    
    tests = [
        test_generate_study_plan,
        test_add_question,
        test_generate_test,
        test_submit_test,
        test_get_study_progress,
        test_get_wrong_questions,
        test_generate_review_plan,
        test_get_learning_stats,
        test_create_reminder,
        test_data_persistence
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print(f"测试结果: {sum(results)}/{len(results)} 通过")
    print("=" * 60)
    
    return all(results)


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
