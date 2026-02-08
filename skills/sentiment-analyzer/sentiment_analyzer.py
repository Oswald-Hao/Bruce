#!/usr/bin/env python3
"""
情感分析系统
基于规则和词典的情感分析工具
"""

import re
import json
from typing import Dict, List, Optional
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
            "好", "棒", "优秀", "优秀", "喜欢", "爱", "满意", "推荐", "值得",
            "优秀", "精彩", "美丽", "漂亮", "开心", "快乐", "幸福", "成功",
            "完美", "出色", "杰出", "卓越", "神奇", "妙", "赞", "顶", "牛",
            "厉害", "给力", "强", "强", "优秀", "不错", "挺好", "太好了",
            "棒极了", "非常好", "好极了", "精彩", "出色", "满意", "喜欢",
            "好评", "五星", "完美", "物超所值", "实惠", "便宜", "值",
            "开心", "兴奋", "激动", "惊喜", "感谢", "感谢", "多谢", "谢谢",
            "支持", "支持", "给力", "给力", "赞", "赞", "强", "强",
            "顺利", "顺利", "成功", "成功", "完成", "完成", "解决", "解决",
            "改善", "改善", "提升", "提升", "优化", "优化", "增强", "增强",
            "高效", "高效", "快速", "快速", "便捷", "便捷", "简单", "简单",
            "易用", "易用", "方便", "方便", "舒适", "舒适", "稳定", "稳定",
            "可靠", "可靠", "安全", "安全", "放心", "放心", "安心", "安心",
        }

        # 中文负面词
        self.zh_negative = {
            "差", "糟糕", "失望", "不满", "讨厌", "恨", "愤怒", "生气", "不满",
            "差劲", "烂", "垃圾", "坑", "骗", "欺诈", "假", "劣质", "低劣",
            "不好", "不行", "不行", "无法", "失败", "错误", "错误", "问题",
            "故障", "故障", "bug", "缺陷", "缺陷", "漏洞", "漏洞", "缺点",
            "不足", "不足", "坏", "坏", "坏掉", "坏掉", "损坏", "损坏",
            "麻烦", "麻烦", "复杂", "复杂", "难用", "难用", "难搞", "难搞",
            "昂贵", "昂贵", "太贵", "太贵", "不值", "不值", "浪费", "浪费",
            "后悔", "后悔", "投诉", "投诉", "举报", "举报", "谴责", "谴责",
            "批评", "批评", "指责", "指责", "质疑", "质疑", "怀疑", "怀疑",
            "难过", "难过", "痛苦", "痛苦", "烦恼", "烦恼", "焦虑", "焦虑",
            "担心", "担心", "害怕", "害怕", "恐惧", "恐惧", "愤怒", "愤怒",
            "郁闷", "郁闷", "抑郁", "抑郁", "悲伤", "悲伤", "哭", "哭",
        }

        # 英文正面词
        self.en_positive = {
            "good", "great", "excellent", "awesome", "amazing", "wonderful",
            "fantastic", "love", "like", "recommend", "perfect", "best",
            "beautiful", "happy", "satisfied", "impressive", "outstanding",
            "brilliant", "superb", "magnificent", "marvelous", "terrific",
            "fabulous", "fantastic", "great", "nice", "cool", "awesome",
            "excellent", "outstanding", "amazing", "wonderful", "fantastic",
            "perfect", "pleased", "delighted", "satisfied", "content",
            "grateful", "thankful", "appreciate", "thanks", "support",
            "helpful", "useful", "effective", "efficient", "smooth",
            "easy", "simple", "convenient", "comfortable", "stable",
            "reliable", "safe", "secure", "trustworthy", "valuable",
            "worth", "affordable", "cheap", "inexpensive", "bargain",
            "excited", "thrilled", "delighted", "pleased", "happy",
            "joy", "joyful", "cheerful", "positive", "optimistic",
            "successful", "complete", "finished", "resolved", "fixed",
            "improved", "better", "enhanced", "optimized", "upgraded",
            "fast", "quick", "rapid", "speedy", "instant",
        }

        # 英文负面词
        self.en_negative = {
            "bad", "terrible", "awful", "horrible", "poor", "worst",
            "hate", "dislike", "disappoint", "unsatisfied", "angry",
            "upset", "frustrated", "annoying", "irritating", "disappointing",
            "waste", "wasteful", "regret", "sorry", "apologize", "apology",
            "fail", "failure", "error", "problem", "issue", "bug",
            "defect", "fault", "flaw", "broken", "damaged", "broken",
            "useless", "worthless", "pointless", "meaningless", "stupid",
            "ridiculous", "absurd", "outrageous", "unacceptable", "unbearable",
            "expensive", "costly", "overpriced", "rip-off", "scam", "fraud",
            "fake", "false", "deceptive", "misleading", "dishonest",
            "complaint", "complain", "report", "condemn", "criticize",
            "blame", "accuse", "suspect", "doubt", "question",
            "sad", "unhappy", "miserable", "depressed", "anxious",
            "worried", "afraid", "scared", "fearful", "angry", "furious",
            "upset", "distressed", "troubled", "concerned", "concerning",
            "disappointed", "let down", "boring", "dull", "tedious",
            "complicated", "complex", "difficult", "hard", "tough",
            "slow", "sluggish", "lagging", "unstable", "unreliable",
        }

        # 中文否定词
        self.zh_negation = {
            "不", "没", "无", "非", "别", "莫", "勿", "未", "没有",
            "不是", "不会", "不能", "不要", "不用", "无须", "无需",
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
            "太": 1.8, "好": 1.5, "很": 1.5, "挺": 1.3,
            "相当": 1.5, "比较": 1.2, "有点": 0.5, "稍微": 0.5,
            # 程度增强（英文）
            "very": 1.8, "extremely": 2.5, "highly": 2.0,
            "really": 1.8, "so": 1.8, "too": 1.8, "quite": 1.5,
            "rather": 1.5, "fairly": 1.2, "somewhat": 0.5,
            "slightly": 0.5, "a bit": 0.5, "a little": 0.5,
        }

    def _is_chinese(self, text: str) -> bool:
        """判断文本是否包含中文"""
        return bool(re.search(r'[\u4e00-\u9fff]', text))

    def _tokenize(self, text: str) -> List[str]:
        """简单分词"""
        # 移除标点符号
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)
        # 分词
        tokens = text.split()
        return tokens

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
        tokens = self._tokenize(text)

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
        negation_flags = [False] * (len(tokens) + 1)

        # 检测否定词
        for i, token in enumerate(tokens):
            if token in negation_dict:
                negation_flags[i] = True
                # 否定词影响后1-2个词
                if i + 1 < len(negation_flags):
                    negation_flags[i + 1] = True
                if i + 2 < len(negation_flags):
                    negation_flags[i + 2] = True

        # 检测情感词
        for i, token in enumerate(tokens):
            is_negated = negation_flags[i]

            # 计算程度副词权重
            degree = 1.0
            if i > 0 and tokens[i - 1] in self.degree_words:
                degree = self.degree_words[tokens[i - 1]]

            if token in positive_dict:
                score = 1.0 * degree
                if is_negated:
                    score = -score
                    negative_tokens.append(token)
                    negative_score += abs(score)
                else:
                    positive_tokens.append(token)
                    positive_score += score

            elif token in negative_dict:
                score = -1.0 * degree
                if is_negated:
                    score = -score
                    positive_tokens.append(token)
                    positive_score += score
                else:
                    negative_tokens.append(token)
                    negative_score += abs(score)

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
            confidence = 0.3  # 无情感词，置信度低

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
