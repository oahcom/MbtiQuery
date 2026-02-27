import hashlib
import json
from datetime import datetime, timedelta

from sqlalchemy import func, Index
from sqlalchemy.orm import validates

from wxcloudrun import db



class BaseModel(db.Model):
    """基础模型混入类"""

    __abstract__ = True

    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    @classmethod
    def get_by_id(cls, id):
        """根据ID获取记录"""
        return cls.query.get(id)

    @classmethod
    def get_all(cls, page=1, per_page=20):
        """分页获取所有记录"""
        return cls.query.paginate(page=page, per_page=per_page, error_out=False)

    def save(self):
        """保存记录"""
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """删除记录"""
        db.session.delete(self)
        db.session.commit()
        return True


class TestResult(BaseModel):
    """测试结果模型 - 增强版"""
    __tablename__ = 'test_results'

    # 用户标识
    user_id = db.Column(db.String(100), nullable=False, index=True)
    session_id = db.Column(db.String(100), nullable=True, index=True)

    # 测试数据
    answers = db.Column(db.Text, nullable=False)  # JSON格式的答案
    answers_hash = db.Column(db.String(64), nullable=True)  # 答案的MD5哈希，用于快速比对

    # 主类型结果
    mbti_type = db.Column(db.String(4), nullable=False, index=True)
    sub_type = db.Column(db.String(10), nullable=True, index=True)

    # 各维度得分
    ei_score = db.Column(db.Integer, nullable=False)
    sn_score = db.Column(db.Integer, nullable=False)
    tf_score = db.Column(db.Integer, nullable=False)
    jp_score = db.Column(db.Integer, nullable=False)

    # 维度倾向程度
    ei_tendency = db.Column(db.String(10), nullable=True)  # 轻微/中等/明显
    sn_tendency = db.Column(db.String(10), nullable=True)
    tf_tendency = db.Column(db.String(10), nullable=True)
    jp_tendency = db.Column(db.String(10), nullable=True)

    # 辅人格得分
    ao_score = db.Column(db.Float, nullable=True)  # A/O维度 (-2~2)
    hc_score = db.Column(db.Float, nullable=True)  # H/C维度 (-2~2)

    # 测试环境信息
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6兼容
    user_agent = db.Column(db.String(255), nullable=True)

    # 完整结果JSON
    result_json = db.Column(db.Text, nullable=True)

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # 复合索引
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
        Index('idx_type_created', 'mbti_type', 'created_at'),
        Index('idx_subtype_created', 'sub_type', 'created_at'),
        Index('idx_user_session', 'user_id', 'session_id'),
    )

    @validates('mbti_type')
    def validate_mbti_type(self, key, value):
        """验证MBTI类型格式"""
        valid_types = ['ISTJ', 'ISFJ', 'INFJ', 'INTJ', 'ISTP', 'ISFP', 'INFP', 'INTP',
                       'ESTP', 'ESFP', 'ENFP', 'ENTP', 'ESTJ', 'ESFJ', 'ENFJ', 'ENTJ']
        if value not in valid_types:
            raise ValueError(f"无效的MBTI类型: {value}")
        return value

    @validates('sub_type')
    def validate_sub_type(self, key, value):
        """验证辅人格类型格式"""
        if value:
            # 格式如: INTJ-A-H
            parts = value.split('-')
            if len(parts) != 3:
                raise ValueError(f"无效的辅人格格式: {value}")
            main_type, ao, hc = parts
            if ao not in ['A', 'O'] or hc not in ['H', 'C']:
                raise ValueError(f"无效的辅人格维度: {value}")
        return value

    def set_answers(self, answers_list):
        """设置答案并计算哈希"""
        self.answers = json.dumps(answers_list)
        # 计算MD5哈希用于快速比对
        answers_str = json.dumps(answers_list, sort_keys=True)
        self.answers_hash = hashlib.md5(answers_str.encode()).hexdigest()

    def get_answers(self):
        """获取答案列表"""
        return json.loads(self.answers) if self.answers else []

    def to_dict(self, include_details=False):
        """转换为字典"""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'mbti_type': self.mbti_type,
            'sub_type': self.sub_type,
            'ei_score': self.ei_score,
            'sn_score': self.sn_score,
            'tf_score': self.tf_score,
            'jp_score': self.jp_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_details:
            result.update({
                'answers': self.get_answers(),
                'answers_hash': self.answers_hash,
                'ei_tendency': self.ei_tendency,
                'sn_tendency': self.sn_tendency,
                'tf_tendency': self.tf_tendency,
                'jp_tendency': self.jp_tendency,
                'ao_score': self.ao_score,
                'hc_score': self.hc_score,
                'ip_address': self.ip_address,
                'user_agent': self.user_agent,
                'result_json': json.loads(self.result_json) if self.result_json else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            })

        return result

    @classmethod
    def get_user_latest(cls, user_id, limit=5):
        """获取用户最新的测试记录"""
        return cls.query.filter_by(user_id=user_id) \
            .order_by(cls.created_at.desc()) \
            .limit(limit) \
            .all()

    @classmethod
    def get_stats_by_type(cls, start_date=None, end_date=None):
        """按类型统计测试结果"""
        query = db.session.query(
            cls.mbti_type,
            func.count(cls.id).label('count')
        )

        if start_date:
            query = query.filter(cls.created_at >= start_date)
        if end_date:
            query = query.filter(cls.created_at <= end_date)

        return query.group_by(cls.mbti_type).all()

    @classmethod
    def get_trend_data(cls, days=30):
        """获取趋势数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        results = db.session.query(
            func.date(cls.created_at).label('date'),
            cls.mbti_type,
            func.count(cls.id).label('count')
        ).filter(
            cls.created_at.between(start_date, end_date)
        ).group_by(
            'date', cls.mbti_type
        ).all()

        return results


class UserProfile(BaseModel):
    """用户画像模型 - 用于追踪用户长期MBTI变化"""
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), unique=True, nullable=False, index=True)

    # 基本信息
    email = db.Column(db.String(120), nullable=True)
    nickname = db.Column(db.String(50), nullable=True)
    birth_year = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(10), nullable=True)

    # 最常出现的MBTI
    primary_type = db.Column(db.String(4), nullable=True)
    primary_sub_type = db.Column(db.String(10), nullable=True)

    # 统计信息
    test_count = db.Column(db.Integer, default=0)

    # 各维度平均分
    avg_ei = db.Column(db.Float, default=0.0)
    avg_sn = db.Column(db.Float, default=0.0)
    avg_tf = db.Column(db.Float, default=0.0)
    avg_jp = db.Column(db.Float, default=0.0)

    # 最后一次测试
    last_test_id = db.Column(db.Integer, db.ForeignKey('test_results.id'))
    last_test_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # 关联
    last_test = db.relationship('TestResult', foreign_keys=[last_test_id])

    def update_stats(self, test_result):
        """更新用户统计"""
        self.test_count += 1
        self.last_test_id = test_result.id
        self.last_test_at = test_result.created_at

        # 更新平均分（使用加权平均）
        total = self.test_count
        self.avg_ei = (self.avg_ei * (total - 1) + test_result.ei_score) / total
        self.avg_sn = (self.avg_sn * (total - 1) + test_result.sn_score) / total
        self.avg_tf = (self.avg_tf * (total - 1) + test_result.tf_score) / total
        self.avg_jp = (self.avg_jp * (total - 1) + test_result.jp_score) / total

        # 更新主要类型（取出现频率最高的）
        type_stats = db.session.query(
            TestResult.mbti_type,
            func.count(TestResult.mbti_type).label('count')
        ).filter(TestResult.user_id == self.user_id) \
            .group_by(TestResult.mbti_type) \
            .order_by(func.count(TestResult.mbti_type).desc()) \
            .first()

        if type_stats:
            self.primary_type = type_stats[0]

        self.save()

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'email': self.email,
            'nickname': self.nickname,
            'primary_type': self.primary_type,
            'primary_sub_type': self.primary_sub_type,
            'test_count': self.test_count,
            'avg_scores': {
                'EI': round(self.avg_ei, 2),
                'SN': round(self.avg_sn, 2),
                'TF': round(self.avg_tf, 2),
                'JP': round(self.avg_jp, 2)
            },
            'last_test_at': self.last_test_at.isoformat() if self.last_test_at else None
        }


class Feedback(BaseModel):
    """用户反馈模型"""
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=True, index=True)
    test_result_id = db.Column(db.Integer, db.ForeignKey('test_results.id'), nullable=True)

    # 反馈类型
    feedback_type = db.Column(db.String(20), nullable=False)  # accurate/inaccurate/suggestion

    # 反馈内容
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=True)  # 1-5星评分

    # 状态
    status = db.Column(db.String(20), default='pending')  # pending/reviewed/resolved

    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 关联
    test_result = db.relationship('TestResult', foreign_keys=[test_result_id])

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'feedback_type': self.feedback_type,
            'content': self.content,
            'rating': self.rating,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
