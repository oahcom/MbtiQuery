import numpy as np
from wxcloudrun.questions import get_all_questions


class MBTICalculator:
    """MBTI结果计算器"""

    def __init__(self):
        self.questions = get_all_questions()

        # 维度映射
        self.dimensions = {
            'EI': {'E': [], 'I': []},
            'SN': {'S': [], 'N': []},
            'TF': {'T': [], 'F': []},
            'JP': {'J': [], 'P': []}
        }

        # 初始化维度题目索引
        self._init_dimension_mapping()

    def _init_dimension_mapping(self):
        """初始化维度映射"""
        for q in self.questions:
            category = q['category']
            dimension = q['dimension']

            if category in self.dimensions and dimension in self.dimensions[category]:
                self.dimensions[category][dimension].append(q['id'])

    def calculate(self, answers):
        """
        计算MBTI结果
        answers: [{'question_id': 1, 'score': 2}, ...]
        """
        # 构建答案字典
        answer_dict = {a['question_id']: a['score'] for a in answers}

        # 计算各维度得分
        ei_score = self._calculate_dimension_score(answer_dict, 'EI')
        sn_score = self._calculate_dimension_score(answer_dict, 'SN')
        tf_score = self._calculate_dimension_score(answer_dict, 'TF')
        jp_score = self._calculate_dimension_score(answer_dict, 'JP')

        # 确定主类型
        mbti_type = self._determine_type(ei_score, sn_score, tf_score, jp_score)

        # 计算倾向程度
        ei_tendency = self._get_tendency_level(ei_score)
        sn_tendency = self._get_tendency_level(sn_score)
        tf_tendency = self._get_tendency_level(tf_score)
        jp_tendency = self._get_tendency_level(jp_score)

        # 计算辅人格
        ao_score, hc_score = self._calculate_sub_dimensions(answer_dict)
        sub_type = self._determine_sub_type(mbti_type, ao_score, hc_score)

        return {
            'type': mbti_type,
            'sub_type': sub_type,
            'scores': {
                'EI': ei_score,
                'SN': sn_score,
                'TF': tf_score,
                'JP': jp_score
            },
            'tendency': {
                'EI': ei_tendency,
                'SN': sn_tendency,
                'TF': tf_tendency,
                'JP': jp_tendency
            },
            'sub_scores': {
                'AO': ao_score,
                'HC': hc_score
            }
        }

    def _calculate_dimension_score(self, answer_dict, dimension):
        """计算单个维度的得分"""
        pos_score = 0
        neg_score = 0

        pos_dim, neg_dim = list(self.dimensions[dimension].keys())

        # 计算正向维度得分
        for q_id in self.dimensions[dimension][pos_dim]:
            if q_id in answer_dict:
                score = answer_dict[q_id]
                # 检查是否需要反向计分
                q = next((q for q in self.questions if q['id'] == q_id), None)
                if q and q.get('reverse_score', False):
                    score = -score
                pos_score += score

        # 计算负向维度得分
        for q_id in self.dimensions[dimension][neg_dim]:
            if q_id in answer_dict:
                score = answer_dict[q_id]
                q = next((q for q in self.questions if q['id'] == q_id), None)
                if q and q.get('reverse_score', False):
                    score = -score
                neg_score += score

        # 返回倾向得分 (正-负)
        return pos_score - neg_score

    def _determine_type(self, ei, sn, tf, jp):
        """确定MBTI类型"""
        type_str = ''

        # E/I
        type_str += 'E' if ei > 0 else 'I'

        # S/N
        type_str += 'S' if sn > 0 else 'N'

        # T/F
        type_str += 'T' if tf > 0 else 'F'

        # J/P
        type_str += 'J' if jp > 0 else 'P'

        return type_str

    def _get_tendency_level(self, score):
        """获取倾向程度"""
        abs_score = abs(score)
        if abs_score <= 8:
            return '轻微'
        elif abs_score <= 16:
            return '中等'
        else:
            return '明显'

    def _calculate_sub_dimensions(self, answer_dict):
        """计算辅人格维度 A/O 和 H/C"""

        # A/O维度：基于决策速度和确定性的题目
        ao_questions = [3, 4, 25, 26, 37, 38, 41, 42, 45, 46, 47, 48]
        ao_scores = []

        for q_id in ao_questions:
            if q_id in answer_dict:
                score = answer_dict[q_id]
                # 部分题目需要反向计分
                if q_id in [4, 26, 38, 42, 46, 48]:  # 犹豫不决倾向的题目
                    score = -score
                ao_scores.append(score)

        # 计算A/O得分 (正为A果断，负为O纠结)
        ao_score = np.mean(ao_scores) if ao_scores else 0

        # H/C维度：基于人际温度的题目
        hc_questions = [1, 2, 5, 6, 8, 10, 27, 28, 31, 32, 33, 34]
        hc_scores = []

        for q_id in hc_questions:
            if q_id in answer_dict:
                score = answer_dict[q_id]
                # 高冷倾向的题目反向计分
                if q_id in [2, 6, 8, 10, 27, 31, 33]:  # 高冷倾向
                    score = -score
                hc_scores.append(score)

        # 计算H/C得分 (正为H温暖，负为C高冷)
        hc_score = np.mean(hc_scores) if hc_scores else 0

        return ao_score, hc_score

    def _determine_sub_type(self, main_type, ao_score, hc_score):
        """确定辅人格类型"""
        # A/O判定
        ao_char = 'A' if ao_score > 0 else 'O'

        # H/C判定
        hc_char = 'H' if hc_score > 0 else 'C'

        return f"{main_type}-{ao_char}-{hc_char}"

    def get_detailed_scores(self, answers):
        """获取每个维度的详细得分（用于分析）"""
        answer_dict = {a['question_id']: a['score'] for a in answers}

        detailed = {}

        for dimension in ['EI', 'SN', 'TF', 'JP']:
            pos_dim, neg_dim = list(self.dimensions[dimension].keys())

            pos_scores = []
            neg_scores = []

            for q_id in self.dimensions[dimension][pos_dim]:
                if q_id in answer_dict:
                    score = answer_dict[q_id]
                    q = next((q for q in self.questions if q['id'] == q_id), None)
                    if q and q.get('reverse_score', False):
                        score = -score
                    pos_scores.append(score)

            for q_id in self.dimensions[dimension][neg_dim]:
                if q_id in answer_dict:
                    score = answer_dict[q_id]
                    q = next((q for q in self.questions if q['id'] == q_id), None)
                    if q and q.get('reverse_score', False):
                        score = -score
                    neg_scores.append(score)

            detailed[dimension] = {
                'positive': pos_scores,
                'negative': neg_scores,
                'positive_sum': sum(pos_scores),
                'negative_sum': sum(neg_scores),
                'total': sum(pos_scores) - sum(neg_scores)
            }

        return detailed