#!/usr/bin/env python3
"""
情感分析系统
基于规则和词典的情感分析工具
"""

import re
import json
from typing import Dict, List, Optional, Set, Tuple
from collections import Counter


class SentimentAnalyzer:
    """情感分析器"""

    def __init__(self):
        """初始化情感分析器"""
        self._load_dictionaries()

    def _load_dictionaries(self):
        """加载情感词典"""
        # 中文正面词
        self.zh_positive = {
            "好", "棒", "优秀", "喜欢", "爱", "满意", "推荐", "值得",
            "精彩", "美丽", "漂亮", "开心", "快乐", "幸福", "成功",
            "完美", "出色", "杰出", "卓越", "神奇", "妙", "赞", "顶", "牛",
            "厉害", "给力", "强", "不错", "挺好", "太好了",
            "棒极了", "非常好", "好极了", "好评", "五星", "物超所值",
            "实惠", "便宜", "值", "兴奋", "激动", "惊喜", "感谢",
            "多谢", "谢谢", "支持", "顺利", "解决", "改善",
            "提升", "优化", "增强", "高效", "快速", "便捷",
            "简单", "易用", "方便", "舒适", "稳定", "可靠",
            "安全", "放心", "安心",
        }

        # 中文负面词
        self.zh_negative = {
            "差", "糟糕", "失望", "不满", "讨厌", "恨", "愤怒", "生气",
            "差劲", "烂", "垃圾", "坑", "骗", "欺诈", "假", "劣质", "低劣",
            "不好", "不行", "无法", "失败", "错误", "问题",
            "故障", "bug", "缺陷", "漏洞", "缺点", "不足",
            "坏", "坏掉", "损坏", "麻烦", "复杂", "难用", "难搞",
            "昂贵", "太贵", "不值", "浪费", "后悔", "投诉",
            "举报", "谴责", "批评", "指责", "质疑", "怀疑",
            "难过", "痛苦", "烦恼", "焦虑", "担心", "害怕",
            "恐惧", "郁闷", "抑郁", "悲伤", "哭",
        }

        # 英文正面词
        self.en_positive = {
            "good", "great", "excellent", "awesome", "amazing", "wonderful",
            "fantastic", "love", "like", "recommend", "perfect", "best",
            "beautiful", "happy", "satisfied", "impressive", "outstanding",
            "brilliant", "superb", "magnificent", "marvelous", "terrific",
            "fabulous", "nice", "cool", "pleased", "delighted", "content",
            "grateful", "thankful", "appreciate", "thanks", "support",
            "helpful", "useful", "effective", "efficient", "smooth",
            "easy", "simple", "convenient", "comfortable", "stable",
            "reliable", "safe", "secure", "trustworthy", "valuable",
            "worth", "affordable", "cheap", "inexpensive", "bargain",
            "excited", "thrilled", "joy", "joyful", "cheerful", "positive",
            "optimistic", "successful", "complete", "finished", "resolved",
            "fixed", "improved", "better", "enhanced", "optimized", "upgraded",
            "fast", "quick", "rapid", "speedy", "instant",
        }

        # 英文负面词
        self.en_negative = {
            "bad", "terrible", "awful", "horrible", "poor", "worst",
            "hate", "dislike", "disappoint", "unsatisfied", "angry",
            "upset", "frustrated", "annoying", "irritating", "disappointing",
            "waste", "wasteful", "regret", "sorry", "apologize", "apology",
            "fail", "failure", "error", "problem", "issue", "bug",
            "defect", "fault", "flaw", "broken", "damaged",
            "useless", "worthless", "pointless", "meaningless", "stupid",
            "ridiculous", "absurd", "outrageous", "unacceptable", "unbearable",
            "expensive", "costly", "overpriced", "rip-off", "scam", "fraud",
            "fake", "false", "deceptive", "misleading", "dishonest",
            "complaint", "complain", "report", "condemn", "criticize",
            "blame", "accuse", "suspect", "doubt", "question",
            "sad", "unhappy", "miserable", "depressed", "anxious",
            "worried", "afraid", "scared", "fearful", "furious",
            "upset", "distressed", "troubled", "concerned", "boring",
            "dull", "tedious", "complicated", "complex", "difficult", "hard",
            "tough", "slow", "sluggish", "lagging", "unstable", "unreliable",
        }

        # 中文否定词
        self.zh_negation = {
            "不", "没", "无", "非", "别", "莫", "勿", "未", "没有",
        }

        # 英文否定词
        self.en_negation = {
            "not", "no", "never", "none", "n't", "don't", "doesn't",
            "didn't", "won't", "wouldn't", "couldn't", "shouldn't",
            "can't", "cannot", "isn't", "aren't", "wasn't", "weren't",
            "without", "lack", "neither", "nor", "nobody", "nothing",
        }

        # 程度副词（增强或减弱情感）
        self.degree_words = {
            # 程度增强（中文）
            "非常": 2.0, "特别": 2.0, "极其": 2.5, "超级": 2.0,
            "太": 1.8, "很": 1.5, "挺": 1.3, "相当": 1.5, "比较": 1.2,
            "有点": 0.5, "稍微": 0.5,
            # 程度增强（英文）
            "very": 1.8, "extremely": 2.5, "highly": 2.0,
            "really": 1.8, "so": 1.8, "too": 1.8, "quite": 1.5,
            "rather": 1.5, "fairly": 1.2, "somewhat": 0.5,
            "slightly": 0.5, "a bit": 0.5, "a little": 0.5,
        }

    def _is_chinese(self, text: str) -> bool:
        """判断文本是否包含中文"""
        return bool(re.search(r'[\u4e00-\u9fff]', text))

    def _tokenize_english(self, text: str) -> List[str]:
        """英文分词"""
        # 移除标点符号
        text = re.sub(r'[^\w\s]', ' ', text)
        # 分词
        tokens = text.split()
        return tokens

    def _find_words(self, text: str, word_set: Set[str]) -> List[Tuple[str, int]]:
        """
        在文本中查找所有匹配的词

        Args:
            text: 文本
            word_set: 词典

        Returns:
            匹配的词列表，每个元素为 (词, 起始位置)
        """
        matches = []

        # 按长度排序，优先匹配长词
        sorted_words = sorted(word_set, key=len, reverse=True)

        for word in sorted_words:
            start = 0
            while True:
                pos = text.find(word, start)
                if pos == -1:
                    break
                matches.append((word, pos))
                start = pos + 1

        # 按位置排序
        matches.sort(key=lambda x: x[1])
        return matches

    def _check_negation(self, text: str, word_pos: int, word_len: int,
                       negation_dict: Set[str]) -> bool:
        """
        检查词是否被否定

        Args:
            text: 文本
            word_pos: 词的起始位置
            word_len: 词的长度
            negation_dict: 否定词典

        Returns:
            是否被否定
        """
        # 检查词前面是否有否定词
        lookbehind = text[:word_pos]

        # 查找最近的否定词
        negation_words = self._find_words(lookbehind, negation_dict)

        if not negation_words:
            return False

        # 找到最近的否定词
        last_negation = negation_words[-1]
        neg_word, neg_pos = last_negation

        # 否定词到目标词的距离（考虑字符数）
        distance = word_pos - (neg_pos + len(neg_word))

        # 如果距离在3个字符内，认为是否定（更严格的距离）
        return distance <= 3

    def _get_degree(self, text: str, word_pos: int) -> float:
        """
        获取词前面的程度副词

        Args:
            text: 文本
            word_pos: 词的起始位置

        Returns:
            程度副词权重
        """
        # 检查词前面的程度副词
        lookbehind = text[:word_pos]

        for word, weight in self.degree_words.items():
            # 查找程度副词是否在词前面
            pos = lookbehind.rfind(word)
            if pos != -1:
                # 检查距离（3个字符内）
                if word_pos - (pos + len(word)) <= 3:
                    return weight

        return 1.0

    def analyze(self, text: str) -> Dict:
        """
        分析单句文本的情感

        Args:
            text: 待分析文本

        Returns:
            情感分析结果字典
        """
        if not text or not text.strip():
            return {
                "label": "neutral",
                "score": 0.0,
                "confidence": 0.0,
                "tokens": []
            }

        text = text.strip().lower()

        # 检测语言
        is_chinese = self._is_chinese(text)

        # 选择词典
        if is_chinese:
            positive_dict = self.zh_positive
            negative_dict = self.zh_negative
            negation_dict = self.zh_negation
        else:
            positive_dict = self.en_positive
            negative_dict = self.en_negative
            negation_dict = self.en_negation

        # 计算情感得分
        positive_score = 0
        negative_score = 0
        positive_tokens = []
        negative_tokens = []

        # 查找所有情感词的位置
        positive_matches = self._find_words(text, positive_dict)
        negative_matches = self._find_words(text, negative_dict)

        # 处理正面词
        for word, pos in positive_matches:
            # 检查是否被否定
            is_negated = self._check_negation(text, pos, len(word), negation_dict)

            # 获取程度副词
            degree = self._get_degree(text, pos)

            score = 1.0 * degree
            if is_negated:
                negative_score += score
                negative_tokens.append(word)
            else:
                positive_score += score
                positive_tokens.append(word)

        # 处理负面词
        for word, pos in negative_matches:
            # 检查是否被否定
            is_negated = self._check_negation(text, pos, len(word), negation_dict)

            # 获取程度副词
            degree = self._get_degree(text, pos)

            score = 1.0 * degree
            if is_negated:
                positive_score += score
                positive_tokens.append(word)
            else:
                negative_score += score
                negative_tokens.append(word)

        # 计算总得分
        total_score = positive_score - negative_score

        # 归一化到[-1, 1]
        if positive_score + negative_score > 0:
            normalized_score = total_score / (positive_score + negative_score)
        else:
            normalized_score = 0.0

        # 确定标签
        if normalized_score > 0.2:
            label = "positive"
        elif normalized_score < -0.2:
            label = "negative"
        else:
            label = "neutral"

        # 计算置信度（基于情感词数量）
        total_sentiment_words = len(positive_tokens) + len(negative_tokens)
        if total_sentiment_words > 0:
            confidence = min(1.0, 0.5 + total_sentiment_words * 0.1)
        else:
            confidence = 0.3

        # 分词
        if is_chinese:
            tokens = list(text)  # 中文按字分
        else:
            tokens = self._tokenize_english(text)

        return {
            "label": label,
            "score": round(normalized_score, 3),
            "confidence": round(confidence, 3),
            "tokens": tokens,
            "positive_tokens": positive_tokens,
            "negative_tokens": negative_tokens,
        }

    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """
        批量分析文本情感

        Args:
            texts: 文本列表

        Returns:
            分析结果列表
        """
        results = []
        for text in texts:
            result = self.analyze(text)
            results.append(result)
        return results

    def analyze_summary(self, texts: List[str]) -> Dict:
        """
        分析并汇总情感

        Args:
            texts: 文本列表

        Returns:
            汇总统计
        """
        results = self.analyze_batch(texts)

        # 统计各类情感数量
        label_counts = Counter(r["label"] for r in results)

        # 计算平均得分
        scores = [r["score"] for r in results]
        avg_score = sum(scores) / len(scores) if scores else 0.0

        # 情感分布
        distribution = {
            "positive": label_counts.get("positive", 0),
            "neutral": label_counts.get("neutral", 0),
            "negative": label_counts.get("negative", 0),
        }

        # 百分比
        total = len(texts)
        if total > 0:
            for key in distribution:
                distribution[key] = round(distribution[key] / total * 100, 2)

        return {
            "total": total,
            "average_score": round(avg_score, 3),
            "distribution": distribution,
            "label_counts": dict(label_counts),
        }

    def analyze_trend(self, texts: List[str]) -> List[Dict]:
        """
        分析情感趋势

        Args:
            texts: 按时间顺序排列的文本列表

        Returns:
            情感趋势数据
        """
        results = []
        for i, text in enumerate(texts):
            result = self.analyze(text)
            result["index"] = i
            result["timestamp"] = i
            results.append(result)
        return results

    def get_dict_info(self) -> Dict:
        """
        获取词典信息

        Returns:
            词典统计信息
        """
        return {
            "zh_positive": len(self.zh_positive),
            "zh_negative": len(self.zh_negative),
            "en_positive": len(self.en_positive),
            "en_negative": len(self.en_negative),
            "zh_negation": len(self.zh_negation),
            "en_negation": len(self.en_negation),
            "degree_words": len(self.degree_words),
        }


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="情感分析系统")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # analyze命令
    analyze_parser = subparsers.add_parser("analyze", help="分析单句文本")
    analyze_parser.add_argument("text", help="待分析文本")

    # batch命令
    batch_parser = subparsers.add_parser("batch", help="批量分析")
    batch_parser.add_argument("input", help="输入文件（每行一条文本）")
    batch_parser.add_argument("output", help="输出文件（JSON格式）")

    # summary命令
    summary_parser = subparsers.add_parser("summary", help="汇总分析")
    summary_parser.add_argument("input", help="输入文件（每行一条文本）")

    # trend命令
    trend_parser = subparsers.add_parser("trend", help="趋势分析")
    trend_parser.add_argument("input", help="输入文件（每行一条文本）")

    # dict命令
    subparsers.add_parser("dict", help="查看词典信息")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    sa = SentimentAnalyzer()

    if args.command == "analyze":
        result = sa.analyze(args.text)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "batch":
        with open(args.input, 'r', encoding='utf-8') as f:
            texts = [line.strip() for line in f if line.strip()]

        results = sa.analyze_batch(texts)

        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"✓ 分析完成，共处理{len(results)}条文本")

    elif args.command == "summary":
        with open(args.input, 'r', encoding='utf-8') as f:
            texts = [line.strip() for line in f if line.strip()]

        summary = sa.analyze_summary(texts)
        print(json.dumps(summary, indent=2, ensure_ascii=False))

    elif args.command == "trend":
        with open(args.input, 'r', encoding='utf-8') as f:
            texts = [line.strip() for line in f if line.strip()]

        trend = sa.analyze_trend(texts)
        print(json.dumps(trend, indent=2, ensure_ascii=False))

    elif args.command == "dict":
        dict_info = sa.get_dict_info()
        print(json.dumps(dict_info, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
