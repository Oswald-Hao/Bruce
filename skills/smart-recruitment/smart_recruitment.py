#!/usr/bin/env python3
"""
智能招聘系统 (Smart Recruitment System)
智能简历筛选、面试安排、人才匹配、招聘流程管理
"""

import json
import os
import re
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import PyPDF2
    import docx
except ImportError:
    PyPDF2 = None
    docx = None


class ResumeParser:
    """简历解析器"""

    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """解析PDF简历"""
        if PyPDF2 is None:
            raise ImportError("PyPDF2 not installed. Run: pip install PyPDF2")

        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text

    @staticmethod
    def parse_word(file_path: str) -> str:
        """解析Word简历"""
        if docx is None:
            raise ImportError("python-docx not installed. Run: pip install python-docx")

        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text

    @staticmethod
    def parse_text(file_path: str) -> str:
        """解析文本简历"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def parse(file_path: str) -> Dict:
        """解析简历文件，返回结构化数据"""
        file_ext = Path(file_path).suffix.lower()

        if file_ext == '.pdf':
            text = ResumeParser.parse_pdf(file_path)
        elif file_ext in ['.doc', '.docx']:
            text = ResumeParser.parse_word(file_path)
        else:
            text = ResumeParser.parse_text(file_path)

        # 提取关键信息
        data = {
            'name': ResumeParser._extract_name(text),
            'email': ResumeParser._extract_email(text),
            'phone': ResumeParser._extract_phone(text),
            'experience': ResumeParser._extract_experience(text),
            'education': ResumeParser._extract_education(text),
            'skills': ResumeParser._extract_skills(text),
            'raw_text': text
        }
        return data

    @staticmethod
    def _extract_name(text: str) -> Optional[str]:
        """提取姓名"""
        # 简单的姓名提取逻辑
        lines = text.split('\n')
        if lines:
            name_line = lines[0].strip()
            if len(name_line) <= 10 and not name_line.isdigit():
                return name_line
        return None

    @staticmethod
    def _extract_email(text: str) -> Optional[str]:
        """提取邮箱"""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        return match.group() if match else None

    @staticmethod
    def _extract_phone(text: str) -> Optional[str]:
        """提取电话"""
        phone_pattern = r'(?:\+86)?1[3-9]\d{9}'
        match = re.search(phone_pattern, text)
        return match.group() if match else None

    @staticmethod
    def _extract_experience(text: str) -> int:
        """提取工作年限"""
        # 查找工作年限相关描述
        patterns = [
            r'工作[经验|年限|时间][：:\s]*(\d+)\s*年',
            r'(\d+)\s*年[工作经验|工作经验|工作经验|经验|工作时间]',
            r'(\d+)\s*years?\s*(of)?\s*experience'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))
        return 0

    @staticmethod
    def _extract_education(text: str) -> List[str]:
        """提取教育信息"""
        education_keywords = ['本科', '硕士', '博士', '大专', '高中', 'Bachelor', 'Master', 'PhD']
        found = []
        for keyword in education_keywords:
            if keyword in text:
                found.append(keyword)
        return found

    @staticmethod
    def _extract_skills(text: str) -> List[str]:
        """提取技能"""
        # 常见技能关键词
        skill_keywords = [
            'Python', 'Java', 'JavaScript', 'C++', 'Go', 'Rust', 'PHP', 'Ruby',
            'React', 'Vue', 'Angular', 'Spring', 'Django', 'Flask', 'Express',
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Docker', 'Kubernetes',
            'Git', 'Linux', 'AWS', 'Azure', 'GCP', '机器学习', '深度学习',
            '数据分析', '爬虫', '自动化', '测试', '项目管理', '产品经理'
        ]
        found = []
        for skill in skill_keywords:
            if skill in text:
                found.append(skill)
        return found


class CandidateManager:
    """候选人管理"""

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.candidates_file = self.data_dir / 'candidates.json'
        self.interviews_file = self.data_dir / 'interviews.json'
        self.candidates = self._load_candidates()
        self.interviews = self._load_interviews()

    def _load_candidates(self) -> List[Dict]:
        """加载候选人数据"""
        if self.candidates_file.exists():
            with open(self.candidates_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_candidates(self):
        """保存候选人数据"""
        with open(self.candidates_file, 'w', encoding='utf-8') as f:
            json.dump(self.candidates, f, ensure_ascii=False, indent=2)

    def _load_interviews(self) -> List[Dict]:
        """加载面试数据"""
        if self.interviews_file.exists():
            with open(self.interviews_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_interviews(self):
        """保存面试数据"""
        with open(self.interviews_file, 'w', encoding='utf-8') as f:
            json.dump(self.interviews, f, ensure_ascii=False, indent=2)

    def add_candidate(self, name: str, resume_path: str, position: str,
                     tags: List[str] = None) -> Dict:
        """添加候选人"""
        # 解析简历
        resume_data = ResumeParser.parse(resume_path)

        candidate = {
            'id': len(self.candidates) + 1,
            'name': name,
            'email': resume_data.get('email'),
            'phone': resume_data.get('phone'),
            'experience_years': resume_data.get('experience', 0),
            'education': resume_data.get('education', []),
            'skills': resume_data.get('skills', []),
            'position': position,
            'resume_path': resume_path,
            'resume_data': resume_data,
            'tags': tags or [],
            'status': 'pending',  # pending, interviewing, offered, rejected
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        self.candidates.append(candidate)
        self._save_candidates()
        return candidate

    def get_candidate(self, candidate_id: int) -> Optional[Dict]:
        """获取候选人信息"""
        for candidate in self.candidates:
            if candidate['id'] == candidate_id:
                return candidate
        return None

    def update_candidate(self, candidate_id: int, **kwargs) -> bool:
        """更新候选人信息"""
        candidate = self.get_candidate(candidate_id)
        if not candidate:
            return False
        candidate.update(kwargs)
        candidate['updated_at'] = datetime.now().isoformat()
        self._save_candidates()
        return True

    def search_candidates(self, keyword: str = None, min_experience: int = None,
                          required_skills: List[str] = None, position: str = None) -> List[Dict]:
        """搜索候选人"""
        results = []

        for candidate in self.candidates:
            match = True

            # 关键词匹配
            if keyword:
                text = f"{candidate['name']} {candidate['resume_data'].get('raw_text', '')}"
                if keyword.lower() not in text.lower():
                    match = False

            # 经验匹配
            if min_experience and candidate['experience_years'] < min_experience:
                match = False

            # 技能匹配
            if required_skills:
                candidate_skills = set(s.lower() for s in candidate['skills'])
                required = set(s.lower() for s in required_skills)
                if not required.issubset(candidate_skills):
                    match = False

            # 职位匹配
            if position and position.lower() not in candidate['position'].lower():
                match = False

            if match:
                results.append(candidate)

        return results

    def rate_candidate(self, candidate_id: int, round_name: str, score: int,
                       feedback: str = None, interviewer: str = None) -> bool:
        """面试评分"""
        candidate = self.get_candidate(candidate_id)
        if not candidate:
            return False

        interview = {
            'id': len(self.interviews) + 1,
            'candidate_id': candidate_id,
            'round': round_name,
            'score': score,
            'feedback': feedback,
            'interviewer': interviewer,
            'created_at': datetime.now().isoformat()
        }

        self.interviews.append(interview)
        self._save_interviews()

        # 更新候选人状态
        candidate['status'] = 'interviewing'
        candidate['updated_at'] = datetime.now().isoformat()
        self._save_candidates()

        return True

    def schedule_interview(self, candidate_id: int, datetime_str: str,
                           round_name: str, interviewer: str) -> bool:
        """安排面试"""
        candidate = self.get_candidate(candidate_id)
        if not candidate:
            return False

        interview_time = datetime.fromisoformat(datetime_str)

        interview = {
            'id': len(self.interviews) + 1,
            'candidate_id': candidate_id,
            'round': round_name,
            'scheduled_time': datetime_str,
            'interviewer': interviewer,
            'status': 'scheduled',
            'created_at': datetime.now().isoformat()
        }

        self.interviews.append(interview)
        self._save_interviews()

        # 更新候选人状态
        candidate['status'] = 'interviewing'
        candidate['updated_at'] = datetime.now().isoformat()
        self._save_candidates()

        return True

    def get_candidate_interviews(self, candidate_id: int) -> List[Dict]:
        """获取候选人所有面试记录"""
        return [i for i in self.interviews if i['candidate_id'] == candidate_id]

    def calculate_score(self, candidate: Dict, requirements: Dict) -> float:
        """计算候选人匹配分数"""
        score = 0.0
        max_score = 0.0

        # 经验分数 (30%)
        max_score += 30
        min_exp = requirements.get('min_experience', 0)
        exp_years = candidate['experience_years']
        if exp_years >= min_exp:
            exp_score = min(30, (exp_years / min_exp) * 20 if min_exp > 0 else 30)
            score += exp_score

        # 技能匹配 (40%)
        max_score += 40
        required_skills = requirements.get('required_skills', [])
        candidate_skills = set(s.lower() for s in candidate['skills'])
        required = set(s.lower() for s in required_skills)
        if required:
            matched = len(required & candidate_skills)
            skill_score = (matched / len(required)) * 40
            score += skill_score
        else:
            score += 40

        # 学历匹配 (15%)
        max_score += 15
        education_level = requirements.get('education_level')
        if education_level:
            education_map = {'高中': 1, '大专': 2, '本科': 3, '硕士': 4, '博士': 5}
            for edu in candidate['education']:
                if edu in education_map and education_map[edu] >= education_map.get(education_level, 0):
                    score += 15
                    break

        # 关键词匹配 (15%)
        max_score += 15
        keywords = requirements.get('keywords', [])
        if keywords:
            text = candidate['resume_data'].get('raw_text', '').lower()
            matched = sum(1 for kw in keywords if kw.lower() in text)
            keyword_score = (matched / len(keywords)) * 15
            score += keyword_score
        else:
            score += 15

        return score

    def rank_candidates(self, requirements: Dict) -> List[Tuple[Dict, float]]:
        """根据要求对候选人排名"""
        scored = []
        for candidate in self.candidates:
            if candidate['status'] != 'rejected':
                score = self.calculate_score(candidate, requirements)
                scored.append((candidate, score))

        # 按分数降序排序
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    def get_stats(self, period: str = 'all') -> Dict:
        """获取招聘统计数据"""
        now = datetime.now()
        if period == 'week':
            start_date = now - timedelta(weeks=1)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        else:
            start_date = None

        # 过滤期间的候选人
        if start_date:
            candidates = [c for c in self.candidates
                         if datetime.fromisoformat(c['created_at']) >= start_date]
            interviews = [i for i in self.interviews
                         if datetime.fromisoformat(i['created_at']) >= start_date]
        else:
            candidates = self.candidates
            interviews = self.interviews

        stats = {
            'total_candidates': len(candidates),
            'by_status': {},
            'by_position': {},
            'total_interviews': len(interviews),
            'avg_score': 0.0,
            'conversion_rate': 0.0
        }

        # 状态统计
        for candidate in candidates:
            status = candidate['status']
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1

        # 职位统计
        for candidate in candidates:
            position = candidate['position']
            stats['by_position'][position] = stats['by_position'].get(position, 0) + 1

        # 平均分数
        scored_interviews = [i for i in interviews if i.get('score')]
        if scored_interviews:
            stats['avg_score'] = sum(i['score'] for i in scored_interviews) / len(scored_interviews)

        # 转化率（已录用/总数）
        offered = stats['by_status'].get('offered', 0)
        if stats['total_candidates'] > 0:
            stats['conversion_rate'] = (offered / stats['total_candidates']) * 100

        return stats

    def export_data(self, format: str = 'json', output_path: str = None) -> str:
        """导出数据"""
        data = {
            'candidates': self.candidates,
            'interviews': self.interviews,
            'exported_at': datetime.now().isoformat()
        }

        if output_path is None:
            output_path = os.path.join(self.data_dir, f'export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{format}')

        if format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        elif format == 'csv':
            import csv
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'id', 'name', 'email', 'phone', 'position',
                    'experience_years', 'status', 'created_at'
                ])
                writer.writeheader()
                writer.writerows([{k: c.get(k) for k in writer.fieldnames} for c in self.candidates])

        return output_path


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python smart_recruitment.py <command> [options]")
        print("\nCommands:")
        print("  add-candidate  - Add new candidate")
        print("  search         - Search candidates")
        print("  rate           - Rate candidate interview")
        print("  schedule       - Schedule interview")
        print("  rank           - Rank candidates")
        print("  stats          - Show recruitment statistics")
        print("  export         - Export data")
        print("  talent-pool    - View talent pool by tags")
        sys.exit(1)

    manager = CandidateManager()
    command = sys.argv[1]

    if command == 'add-candidate':
        if len(sys.argv) < 5:
            print("Usage: python smart_recruitment.py add-candidate --name <name> --resume <path> --position <position> [--tags tag1,tag2]")
            sys.exit(1)

        name = sys.argv[sys.argv.index('--name') + 1]
        resume = sys.argv[sys.argv.index('--resume') + 1]
        position = sys.argv[sys.argv.index('--position') + 1]
        tags = sys.argv[sys.argv.index('--tags') + 1].split(',') if '--tags' in sys.argv else None

        candidate = manager.add_candidate(name, resume, position, tags)
        print(f"✓ Candidate added: {candidate['name']} (ID: {candidate['id']})")

    elif command == 'search':
        keyword = sys.argv[sys.argv.index('--keyword') + 1] if '--keyword' in sys.argv else None
        min_exp = int(sys.argv[sys.argv.index('--min-experience') + 1]) if '--min-experience' in sys.argv else None
        skills = sys.argv[sys.argv.index('--skills') + 1].split(',') if '--skills' in sys.argv else None
        position = sys.argv[sys.argv.index('--position') + 1] if '--position' in sys.argv else None

        candidates = manager.search_candidates(keyword, min_exp, skills, position)
        print(f"Found {len(candidates)} candidates:")
        for c in candidates:
            print(f"  - {c['name']} (ID: {c['id']}) | {c['position']} | {c['experience_years']} years exp | Skills: {', '.join(c['skills'][:5])}")

    elif command == 'rate':
        candidate_id = int(sys.argv[sys.argv.index('--id') + 1])
        round_name = sys.argv[sys.argv.index('--round') + 1]
        score = int(sys.argv[sys.argv.index('--score') + 1])
        feedback = sys.argv[sys.argv.index('--feedback') + 1] if '--feedback' in sys.argv else None
        interviewer = sys.argv[sys.argv.index('--interviewer') + 1] if '--interviewer' in sys.argv else None

        manager.rate_candidate(candidate_id, round_name, score, feedback, interviewer)
        print(f"✓ Rated candidate {candidate_id}: {score}/100")

    elif command == 'schedule':
        candidate_id = int(sys.argv[sys.argv.index('--id') + 1])
        datetime_str = sys.argv[sys.argv.index('--datetime') + 1]
        round_name = sys.argv[sys.argv.index('--round') + 1]
        interviewer = sys.argv[sys.argv.index('--interviewer') + 1]

        manager.schedule_interview(candidate_id, datetime_str, round_name, interviewer)
        print(f"✓ Interview scheduled for candidate {candidate_id}")

    elif command == 'rank':
        print("Ranking candidates based on requirements:")
        print("(Using default requirements: min_experience=3, required_skills=['Python'])")

        requirements = {
            'min_experience': 3,
            'required_skills': ['Python'],
            'keywords': []
        }

        ranked = manager.rank_candidates(requirements)
        for candidate, score in ranked[:10]:
            print(f"  {score:.1f} - {candidate['name']} (ID: {candidate['id']}) | {candidate['position']}")

    elif command == 'stats':
        period = sys.argv[sys.argv.index('--period') + 1] if '--period' in sys.argv else 'all'
        stats = manager.get_stats(period)

        print(f"\n📊 Recruitment Statistics ({period}):")
        print(f"  Total candidates: {stats['total_candidates']}")
        print(f"  By status: {stats['by_status']}")
        print(f"  By position: {stats['by_position']}")
        print(f"  Total interviews: {stats['total_interviews']}")
        print(f"  Average score: {stats['avg_score']:.1f}/100")
        print(f"  Conversion rate: {stats['conversion_rate']:.1f}%")

    elif command == 'export':
        format_type = sys.argv[sys.argv.index('--format') + 1] if '--format' in sys.argv else 'json'
        output = sys.argv[sys.argv.index('--output') + 1] if '--output' in sys.argv else None
        path = manager.export_data(format_type, output)
        print(f"✓ Data exported to: {path}")

    elif command == 'talent-pool':
        tag = sys.argv[sys.argv.index('--tag') + 1] if '--tag' in sys.argv else None

        candidates = [c for c in manager.candidates if not tag or tag in c['tags']]
        print(f"\n🎯 Talent Pool ({len(candidates)} candidates):")
        for c in candidates:
            print(f"  - {c['name']} | {c['position']} | Skills: {', '.join(c['skills'][:5])} | Tags: {', '.join(c['tags'])}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
