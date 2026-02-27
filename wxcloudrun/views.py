import hashlib
import json
from datetime import datetime, timedelta
from flask import request, jsonify
from sqlalchemy import func

from run import app
from wxcloudrun import db
from wxcloudrun.mbti_calculator import MBTICalculator
from wxcloudrun.model import TestResult, UserProfile, Feedback
from wxcloudrun.questions import get_all_questions
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
from wxcloudrun.results import get_result_description

# 初始化MBTI计算器
calculator = MBTICalculator()


# ==================== API路由 ====================

@app.route('/api/questions', methods=['GET'])
def get_questions():
    """获取所有题目"""
    try:
        questions = get_all_questions()
        return jsonify({
            'code': 200,
            'data': questions,
            'message': '获取题目成功'
        })
    except Exception as e:
        app.logger.error(f'获取题目失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取题目失败：{str(e)}'
        }), 500


@app.route('/api/test/submit', methods=['POST'])
def submit_test():
    """提交测试答案并计算结果"""
    try:
        data = request.get_json()

        if not data or 'answers' not in data:
            return jsonify({
                'code': 400,
                'message': '请提供答案数据'
            }), 400

        answers = data['answers']
        user_id = data.get('user_id', 'anonymous')
        session_id = data.get('session_id', None)

        # 获取客户端信息
        ip_address = request.remote_addr
        user_agent = request.user_agent.string if request.user_agent else None

        # 验证答案格式
        if not isinstance(answers, list) or len(answers) != 48:
            return jsonify({
                'code': 400,
                'message': '答案必须是48个问题的列表'
            }), 400

        # 检查是否重复提交（相同答案）
        answers_str = json.dumps(answers, sort_keys=True)
        answers_hash = hashlib.md5(answers_str.encode()).hexdigest()

        existing = TestResult.query.filter_by(
            user_id=user_id,
            answers_hash=answers_hash
        ).first()

        if existing and (datetime.now() - existing.created_at) < timedelta(minutes=5):
            return jsonify({
                'code': 429,
                'message': '请勿重复提交相同的答案',
                'data': {'existing_id': existing.id}
            }), 429

        # 计算MBTI结果
        result = calculator.calculate(answers)

        # 获取结果描述
        description = get_result_description(result['type'])

        # 合并结果
        full_result = {
            **result,
            'description': description,
            'timestamp': datetime.now().isoformat()
        }

        # 保存到数据库
        test_result = TestResult(
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            mbti_type=result['type'],
            sub_type=result.get('sub_type', ''),
            ei_score=result['scores']['EI'],
            sn_score=result['scores']['SN'],
            tf_score=result['scores']['TF'],
            jp_score=result['scores']['JP'],
            ei_tendency=result['tendency']['EI'],
            sn_tendency=result['tendency']['SN'],
            tf_tendency=result['tendency']['TF'],
            jp_tendency=result['tendency']['JP'],
            ao_score=result['sub_scores']['AO'],
            hc_score=result['sub_scores']['HC'],
            result_json=json.dumps(full_result, ensure_ascii=False)
        )

        # 设置答案
        test_result.set_answers(answers)

        # 保存
        db.session.add(test_result)

        # 更新用户画像
        if user_id != 'anonymous':
            user_profile = UserProfile.query.filter_by(user_id=user_id).first()
            if not user_profile:
                user_profile = UserProfile(user_id=user_id)
                db.session.add(user_profile)

            # 先flush以获取test_result的id
            db.session.flush()
            user_profile.update_stats(test_result)

        db.session.commit()

        app.logger.info(f'用户 {user_id} 完成测试，结果为 {result["type"]}')

        return jsonify({
            'code': 200,
            'data': {
                'test_id': test_result.id,
                'result': full_result
            },
            'message': '测试完成'
        })

    except Exception as e:
        db.session.rollback()
        app.logger.error(f'提交测试失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'提交失败：{str(e)}'
        }), 500


@app.route('/api/test/history/<user_id>', methods=['GET'])
def get_history(user_id):
    """获取用户的历史测试记录"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        pagination = TestResult.query.filter_by() \
            .order_by(TestResult.created_at.desc()) \
            .paginate(page=page, per_page=per_page, error_out=False)

        history = [r.to_dict() for r in pagination.items]

        return jsonify({
            'code': 200,
            'data': {
                'items': history,
                'total': pagination.total,
                'page': page,
                'pages': pagination.pages,
                'per_page': per_page
            },
            'message': '获取历史记录成功'
        })

    except Exception as e:
        app.logger.error(f'获取历史记录失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取历史记录失败：{str(e)}'
        }), 500


@app.route('/api/test/detail/<int:test_id>', methods=['GET'])
def get_test_detail(test_id):
    """获取测试详情"""
    try:
        test_result = TestResult.get_by_id(test_id)
        if not test_result:
            return jsonify({
                'code': 404,
                'message': '测试记录不存在'
            }), 404

        return jsonify({
            'code': 200,
            'data': test_result.to_dict(include_details=True),
            'message': '获取详情成功'
        })

    except Exception as e:
        app.logger.error(f'获取测试详情失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取详情失败：{str(e)}'
        }), 500


@app.route('/api/test/stats', methods=['GET'])
def get_stats():
    """获取测试统计信息"""
    try:
        # 总体统计
        total_tests = TestResult.query.count()

        # 类型分布
        type_distribution = TestResult.get_stats_by_type()

        # 今日统计
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = TestResult.query.filter(TestResult.created_at >= today_start).count()

        # 辅人格分布
        sub_type_stats = db.session.query(
            TestResult.sub_type,
            func.count(TestResult.sub_type).label('count')
        ).filter(TestResult.sub_type.isnot(None)) \
            .group_by(TestResult.sub_type) \
            .order_by(func.count(TestResult.sub_type).desc()) \
            .limit(10).all()

        distribution = {t[0]: t[1] for t in type_distribution}
        sub_distribution = {st[0]: st[1] for st in sub_type_stats}

        return jsonify({
            'code': 200,
            'data': {
                'total_tests': total_tests,
                'today_tests': today_count,
                'type_distribution': distribution,
                'sub_type_distribution': sub_distribution,
                'unique_users': TestResult.query.distinct(TestResult.user_id).count()
            },
            'message': '获取统计成功'
        })

    except Exception as e:
        app.logger.error(f'获取统计失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取统计失败：{str(e)}'
        }), 500


@app.route('/api/test/trend', methods=['GET'])
def get_trend():
    """获取趋势数据"""
    try:
        days = request.args.get('days', 30, type=int)
        trend_data = TestResult.get_trend_data(days)

        # 格式化数据
        result = {}
        for date, mbti_type, count in trend_data:
            date_str = date.strftime('%Y-%m-%d')
            if date_str not in result:
                result[date_str] = {}
            result[date_str][mbti_type] = count

        return jsonify({
            'code': 200,
            'data': result,
            'message': '获取趋势成功'
        })

    except Exception as e:
        app.logger.error(f'获取趋势失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取趋势失败：{str(e)}'
        }), 500


@app.route('/api/user/<user_id>/profile', methods=['GET'])
def get_user_profile(user_id):
    """获取用户画像"""
    try:
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            return jsonify({
                'code': 404,
                'message': '用户不存在'
            }), 404

        return jsonify({
            'code': 200,
            'data': profile.to_dict(),
            'message': '获取成功'
        })

    except Exception as e:
        app.logger.error(f'获取用户画像失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取失败：{str(e)}'
        }), 500


@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """提交反馈"""
    try:
        data = request.get_json()

        feedback = Feedback(
            user_id=data.get('user_id'),
            test_result_id=data.get('test_result_id'),
            feedback_type=data.get('feedback_type'),
            content=data.get('content'),
            rating=data.get('rating'),
            ip_address=request.remote_addr
        )

        feedback.save()

        return jsonify({
            'code': 200,
            'data': {'id': feedback.id},
            'message': '反馈提交成功'
        })

    except Exception as e:
        app.logger.error(f'提交反馈失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'提交失败：{str(e)}'
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        # 测试数据库连接
        db.session.execute('SELECT 1')
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'

    return jsonify({
        'code': 200,
        'status': 'healthy',
        'database': db_status,
        'timestamp': datetime.now().isoformat(),
        'message': 'MBTI API服务正常运行'
    })