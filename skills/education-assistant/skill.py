#!/usr/bin/env python3
"""
教育辅助系统 - Education Assistant

功能：
- 智能学习计划生成
- 知识测试和评估
- 学习进度跟踪
- 错题本和知识巩固
- 学习资料推荐
- 学习提醒和打卡
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
import random


@dataclass
class StudyPlan:
    """学习计划"""
    subject: str
    topic: str
    duration: int  # 分钟
    difficulty: str
    resources: List[str]
    tasks: List[str]
    notes: str


@dataclass
class Question:
    """测试题目"""
    id: str
    subject: str
    topic: str
    question: str
    options: List[str]
    correct_answer: str
    explanation: str
    difficulty: str


@dataclass
class TestResult:
    """测试结果"""
    test_id: str
    subject: str
    date: str
    score: float
    total: int
    correct: int
    wrong_questions: List[str]
    time_spent: int  # 秒


class EducationAssistant:
    """教育辅助系统 - 智能学习和测试系统"""

    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化教育辅助系统

        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.data_dir = Path(self.config.get('data_dir', './education_data'))
        self.data_dir.mkdir(exist_ok=True)
        
        self.study_plans_file = self.data_dir / 'study_plans.json'
        self.questions_file = self.data_dir / 'questions.json'
        self.test_results_file = self.data_dir / 'test_results.json'
        self.progress_file = self.data_dir / 'progress.json'
        
        self.study_plans = self._load_json(self.study_plans_file, [])
        self.questions = self._load_json(self.questions_file, [])
        self.test_results = self._load_json(self.test_results_file, [])
        self.progress = self._load_json(self.progress_file, {})

    def _load_json(self, file_path: Path, default: Any = None):
        """加载JSON文件"""
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default

    def _save_json(self, file_path: Path, data: Any):
        """保存JSON文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def generate_study_plan(self, subject: str, topics: List[str], 
                           difficulty: str = 'medium', 
                           total_hours: int = 10) -> StudyPlan:
        """
        生成学习计划

        Args:
            subject: 学科
            topics: 主题列表
            difficulty: 难度（easy/medium/hard）
            total_hours: 总学习小时数

        Returns:
            学习计划
        """
        # 计算每个主题的时间分配
        topics_count = len(topics)
        hours_per_topic = total_hours / topics_count
        
        # 生成学习任务
        tasks = []
        for i, topic in enumerate(topics):
            tasks.extend([
                f"{i*2+1}. 学习{topic}的基础概念（{hours_per_topic/2:.1f}小时）",
                f"{i*2+2}. 完成{topic}相关练习（{hours_per_topic/2:.1f}小时）"
            ])
        
        # 推荐学习资源
        resources = self._get_recommended_resources(subject, difficulty)
        
        plan = StudyPlan(
            subject=subject,
            topic=', '.join(topics),
            duration=total_hours * 60,  # 转换为分钟
            difficulty=difficulty,
            resources=resources,
            tasks=tasks,
            notes=f"建议每天学习{total_hours/7:.1f}小时，分7天完成"
        )
        
        # 保存计划
        plan_dict = asdict(plan)
        plan_dict['created_at'] = datetime.now().isoformat()
        self.study_plans.append(plan_dict)
        self._save_json(self.study_plans_file, self.study_plans)
        
        return plan

    def _get_recommended_resources(self, subject: str, difficulty: str) -> List[str]:
        """获取推荐的学习资源"""
        resource_map = {
            '编程': [
                '《Python编程：从入门到实践》',
                'LeetCode在线编程练习',
                'GitHub开源项目学习'
            ],
            '数学': [
                'Khan Academy在线课程',
                'MIT OpenCourseWare',
                '《普林斯顿微积分读本》'
            ],
            '英语': [
                'Duolingo语言学习',
                'BBC Learning English',
                '《新概念英语》系列'
            ],
            'AI': [
                'CS231n计算机视觉课程',
                '《深度学习》- Ian Goodfellow',
                'Hugging Face实战教程'
            ],
            '数据科学': [
                'Kaggle竞赛练习',
                '《利用Python进行数据分析》',
                'DataCamp在线课程'
            ]
        }
        
        return resource_map.get(subject, [
            f'{subject}相关在线课程',
            f'{subject}专业书籍推荐',
            f'{subject}实践项目'
        ])

    def add_question(self, question: str, options: List[str], 
                     correct_answer: str, explanation: str,
                     subject: str, topic: str, 
                     difficulty: str = 'medium') -> str:
        """
        添加测试题目

        Args:
            question: 题目
            options: 选项
            correct_answer: 正确答案
            explanation: 解释
            subject: 学科
            topic: 主题
            difficulty: 难度

        Returns:
            题目ID
        """
        question_id = f"{subject}_{topic}_{len(self.questions)+1}_{int(datetime.now().timestamp())}"
        
        new_question = Question(
            id=question_id,
            subject=subject,
            topic=topic,
            question=question,
            options=options,
            correct_answer=correct_answer,
            explanation=explanation,
            difficulty=difficulty
        )
        
        self.questions.append(asdict(new_question))
        self._save_json(self.questions_file, self.questions)
        
        return question_id

    def generate_test(self, subject: str, topic: str = None, 
                      difficulty: str = None, 
                      count: int = 10) -> List[Question]:
        """
        生成测试题目

        Args:
            subject: 学科
            topic: 主题（可选）
            difficulty: 难度（可选）
            count: 题目数量

        Returns:
            题目列表
        """
        filtered_questions = [
            q for q in self.questions 
            if q['subject'] == subject
            and (topic is None or q['topic'] == topic)
            and (difficulty is None or q['difficulty'] == difficulty)
        ]
        
        if len(filtered_questions) < count:
            # 如果题目不够，返回所有匹配的题目
            return [Question(**q) for q in filtered_questions]
        
        # 随机选择题目
        selected = random.sample(filtered_questions, count)
        return [Question(**q) for q in selected]

    def submit_test(self, test_questions: List[Question], 
                    answers: List[str], 
                    time_spent: int) -> TestResult:
        """
        提交测试答案

        Args:
            test_questions: 测试题目
            answers: 答案
            time_spent: 耗时（秒）

        Returns:
            测试结果
        """
        correct_count = 0
        wrong_question_ids = []
        
        for i, (question, answer) in enumerate(zip(test_questions, answers)):
            if answer == question.correct_answer:
                correct_count += 1
            else:
                wrong_question_ids.append(question.id)
        
        score = (correct_count / len(test_questions)) * 100
        
        result = TestResult(
            test_id=f"test_{int(datetime.now().timestamp())}",
            subject=test_questions[0].subject,
            date=datetime.now().isoformat(),
            score=score,
            total=len(test_questions),
            correct=correct_count,
            wrong_questions=wrong_question_ids,
            time_spent=time_spent
        )
        
        # 保存测试结果
        self.test_results.append(asdict(result))
        self._save_json(self.test_results_file, self.test_results)
        
        # 更新学习进度
        self._update_progress(test_questions[0].subject, score, len(test_questions))
        
        return result

    def _update_progress(self, subject: str, score: float, question_count: int):
        """更新学习进度"""
        if subject not in self.progress:
            self.progress[subject] = {
                'total_tests': 0,
                'total_questions': 0,
                'total_correct': 0,
                'average_score': 0,
                'last_test_date': None
            }
        
        progress = self.progress[subject]
        progress['total_tests'] += 1
        progress['total_questions'] += question_count
        progress['total_correct'] += int((score / 100) * question_count)
        progress['average_score'] = progress['total_correct'] / progress['total_questions'] * 100
        progress['last_test_date'] = datetime.now().isoformat()
        
        self._save_json(self.progress_file, self.progress)

    def get_study_progress(self, subject: str = None) -> Dict[str, Any]:
        """
        获取学习进度

        Args:
            subject: 学科（可选）

        Returns:
            学习进度
        """
        if subject:
            return self.progress.get(subject, {})
        return self.progress

    def get_wrong_questions(self, subject: str = None, 
                           topic: str = None) -> List[Question]:
        """
        获取错题

        Args:
            subject: 学科（可选）
            topic: 主题（可选）

        Returns:
            错题列表
        """
        # 收集所有错题ID
        wrong_question_ids = set()
        for result in self.test_results:
            for qid in result['wrong_questions']:
                wrong_question_ids.add(qid)
        
        # 查找对应的题目
        wrong_questions = []
        for q in self.questions:
            if q['id'] in wrong_question_ids:
                if subject is None or q['subject'] == subject:
                    if topic is None or q['topic'] == topic:
                        wrong_questions.append(Question(**q))
        
        return wrong_questions

    def generate_review_plan(self, subject: str, days: int = 7) -> Dict[str, Any]:
        """
        生成复习计划

        Args:
            subject: 学科
            days: 复习天数

        Returns:
            复习计划
        """
        wrong_questions = self.get_wrong_questions(subject)
        
        # 将错题按主题分组
        topic_questions = {}
        for q in wrong_questions:
            if q.topic not in topic_questions:
                topic_questions[q.topic] = []
            topic_questions[q.topic].append(q)
        
        # 分配复习任务
        daily_tasks = {}
        topics_per_day = max(1, len(topic_questions) // days)
        topics = list(topic_questions.keys())
        
        for day in range(days):
            day_topics = topics[day*topics_per_day:(day+1)*topics_per_day]
            if not day_topics and day == 0:
                # 确保第一天至少有任务
                day_topics = [topics[0]] if topics else []
            
            tasks = []
            for topic in day_topics:
                questions = topic_questions[topic]
                tasks.append({
                    'topic': topic,
                    'question_count': len(questions),
                    'review_time': len(questions) * 5  # 每题5分钟
                })
            
            daily_tasks[f"Day_{day+1}"] = {
                'date': (datetime.now() + timedelta(days=day)).strftime('%Y-%m-%d'),
                'tasks': tasks,
                'total_time': sum(t['review_time'] for t in tasks)
            }
        
        return {
            'subject': subject,
            'wrong_questions_count': len(wrong_questions),
            'review_days': days,
            'daily_tasks': daily_tasks
        }

    def get_learning_stats(self) -> Dict[str, Any]:
        """
        获取学习统计

        Returns:
            学习统计数据
        """
        stats = {
            'total_study_plans': len(self.study_plans),
            'total_questions': len(self.questions),
            'total_tests': len(self.test_results),
            'subjects': list(set(q['subject'] for q in self.questions)),
            'progress_summary': {}
        }
        
        # 计算平均分数
        if self.test_results:
            total_score = sum(r['score'] for r in self.test_results)
            stats['average_score'] = total_score / len(self.test_results)
        
        # 按学科统计
        for subject in stats['subjects']:
            subject_tests = [r for r in self.test_results if r['subject'] == subject]
            if subject_tests:
                subject_scores = [r['score'] for r in subject_tests]
                stats['progress_summary'][subject] = {
                    'test_count': len(subject_tests),
                    'average_score': sum(subject_scores) / len(subject_scores),
                    'highest_score': max(subject_scores),
                    'lowest_score': min(subject_scores)
                }
        
        return stats

    def create_reminder(self, subject: str, topic: str, 
                       time: str, message: str = None) -> Dict[str, Any]:
        """
        创建学习提醒

        Args:
            subject: 学科
            topic: 主题
            time: 时间（HH:MM格式）
            message: 提醒消息

        Returns:
            提醒信息
        """
        if message is None:
            message = f"是时候学习{subject}的{topic}了！加油！"
        
        reminder = {
            'subject': subject,
            'topic': topic,
            'time': time,
            'message': message,
            'created_at': datetime.now().isoformat()
        }
        
        return reminder


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description='教育辅助系统')
    parser.add_argument('action', choices=['plan', 'test', 'progress', 'stats', 'review', 'wrong'])
    parser.add_argument('--subject', help='学科')
    parser.add_argument('--topic', help='主题')
    parser.add_argument('--difficulty', default='medium', help='难度')
    parser.add_argument('--count', type=int, default=10, help='题目数量')
    parser.add_argument('--hours', type=int, default=10, help='学习小时数')
    parser.add_argument('--days', type=int, default=7, help='复习天数')

    args = parser.parse_args()

    assistant = EducationAssistant()

    if args.action == 'plan' and args.subject:
        topics = args.topic.split(',') if args.topic else ['基础概念']
        plan = assistant.generate_study_plan(args.subject, topics, args.difficulty, args.hours)
        print(f"学习计划已生成:")
        print(f"  学科: {plan.subject}")
        print(f"  主题: {plan.topic}")
        print(f"  时长: {plan.duration}分钟")
        print(f"  难度: {plan.difficulty}")
        print(f"  推荐资源:")
        for res in plan.resources:
            print(f"    - {res}")
        print(f"  学习任务:")
        for task in plan.tasks:
            print(f"    {task}")
        print(f"  备注: {plan.notes}")

    elif args.action == 'progress':
        progress = assistant.get_study_progress(args.subject)
        print(f"学习进度:")
        print(json.dumps(progress, indent=2, ensure_ascii=False))

    elif args.action == 'stats':
        stats = assistant.get_learning_stats()
        print(f"学习统计:")
        print(json.dumps(stats, indent=2, ensure_ascii=False))

    elif args.action == 'review' and args.subject:
        review_plan = assistant.generate_review_plan(args.subject, args.days)
        print(f"复习计划:")
        print(json.dumps(review_plan, indent=2, ensure_ascii=False))

    elif args.action == 'wrong':
        wrong_questions = assistant.get_wrong_questions(args.subject, args.topic)
        print(f"错题列表 (共{len(wrong_questions)}题):")
        for i, q in enumerate(wrong_questions, 1):
            print(f"\n{i}. [{q.subject}] {q.topic}")
            print(f"   题目: {q.question}")
            print(f"   答案: {q.correct_answer}")
            print(f"   解释: {q.explanation}")


if __name__ == '__main__':
    main()
