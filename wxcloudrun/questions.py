def get_all_questions():
    """获取所有48道题目"""
    questions = [
        # 第一部分：能量倾向 (E/I) - 1-12题
        {
            "id": 1,
            "text": "在社交聚会中，我总能认识新朋友并感到精力充沛。",
            "dimension": "E",
            "reverse_score": False,
            "category": "EI"
        },
        {
            "id": 2,
            "text": "我需要大量的独处时间来恢复精力。",
            "dimension": "I",
            "reverse_score": False,
            "category": "EI"
        },
        {
            "id": 3,
            "text": "我通常边说话边思考，想到什么说什么。",
            "dimension": "E",
            "reverse_score": False,
            "category": "EI"
        },
        {
            "id": 4,
            "text": "在重要场合发言前，我需要提前准备和思考。",
            "dimension": "I",
            "reverse_score": False,
            "category": "EI"
        },
        {
            "id": 5,
            "text": "我容易被认为是个热情、爽朗的人。",
            "dimension": "E",
            "reverse_score": False,
            "category": "EI"
        },
        {
            "id": 6,
            "text": "别人常说我比较深沉，不太容易了解。",
            "dimension": "I",
            "reverse_score": False,
            "category": "EI"
        },
        {
            "id": 7,
            "text": "如果独处太久，我会感到不安和烦躁。",
            "dimension": "E",
            "reverse_score": True,  # 反向计分：高同意度表示E倾向
            "category": "EI"
        },
        {
            "id": 8,
            "text": "如果没有足够的自处时间，我会感到疲惫和焦虑。",
            "dimension": "I",
            "reverse_score": False,
            "category": "EI"
        },
        {
            "id": 9,
            "text": "我更喜欢群体讨论的氛围。",
            "dimension": "E",
            "reverse_score": False,
            "category": "EI"
        },
        {
            "id": 10,
            "text": "我更喜欢一对一的深度交流。",
            "dimension": "I",
            "reverse_score": False,
            "category": "EI"
        },
        {
            "id": 11,
            "text": "在工作中，我倾向于主动接触同事和客户。",
            "dimension": "E",
            "reverse_score": False,
            "category": "EI"
        },
        {
            "id": 12,
            "text": "在工作中，我更愿意专注于自己的任务，减少打扰。",
            "dimension": "I",
            "reverse_score": False,
            "category": "EI"
        },

        # 第二部分：信息收集 (S/N) - 13-24题
        {
            "id": 13,
            "text": "我注重事实和细节，喜欢具体明确的信息。",
            "dimension": "S",
            "reverse_score": False,
            "category": "SN"
        },
        {
            "id": 14,
            "text": "我对事物的含义和可能性更感兴趣。",
            "dimension": "N",
            "reverse_score": False,
            "category": "SN"
        },
        {
            "id": 15,
            "text": "我倾向于先了解细节，再组合成整体。",
            "dimension": "S",
            "reverse_score": False,
            "category": "SN"
        },
        {
            "id": 16,
            "text": "我倾向于先把握整体，细节可以后谈。",
            "dimension": "N",
            "reverse_score": False,
            "category": "SN"
        },
        {
            "id": 17,
            "text": "我喜欢返回熟悉的地方度假。",
            "dimension": "S",
            "reverse_score": False,
            "category": "SN"
        },
        {
            "id": 18,
            "text": "我喜欢探索从未到达过的新地方。",
            "dimension": "N",
            "reverse_score": False,
            "category": "SN"
        },
        {
            "id": 19,
            "text": "我擅长处理现实中的具体问题。",
            "dimension": "S",
            "reverse_score": False,
            "category": "SN"
        },
        {
            "id": 20,
            "text": "我擅长想象未来的可能性和新概念。",
            "dimension": "N",
            "reverse_score": False,
            "category": "SN"
        },
        {
            "id": 21,
            "text": "我更关注眼前正在发生的事。",
            "dimension": "S",
            "reverse_score": False,
            "category": "SN"
        },
        {
            "id": 22,
            "text": "我更关注未来的发展趋势。",
            "dimension": "N",
            "reverse_score": False,
            "category": "SN"
        },
        {
            "id": 23,
            "text": "我倾向于相信经验和既有的方法。",
            "dimension": "S",
            "reverse_score": False,
            "category": "SN"
        },
        {
            "id": 24,
            "text": "我倾向于相信直觉和新的尝试。",
            "dimension": "N",
            "reverse_score": False,
            "category": "SN"
        },

        # 第三部分：决策方式 (T/F) - 25-36题
        {
            "id": 25,
            "text": "我做决定时主要依据逻辑分析。",
            "dimension": "T",
            "reverse_score": False,
            "category": "TF"
        },
        {
            "id": 26,
            "text": "我做决定时会考虑他人的感受和需求。",
            "dimension": "F",
            "reverse_score": False,
            "category": "TF"
        },
        {
            "id": 27,
            "text": "我更希望别人评价我'公正、有原则'。",
            "dimension": "T",
            "reverse_score": False,
            "category": "TF"
        },
        {
            "id": 28,
            "text": "我更希望别人评价我'善解人意、有同情心'。",
            "dimension": "F",
            "reverse_score": False,
            "category": "TF"
        },
        {
            "id": 29,
            "text": "我认为感情用事容易导致错误。",
            "dimension": "T",
            "reverse_score": False,
            "category": "TF"
        },
        {
            "id": 30,
            "text": "我认为过分理性会让人变得冷漠。",
            "dimension": "F",
            "reverse_score": False,
            "category": "TF"
        },
        {
            "id": 31,
            "text": "在谈判中，我更关注事实和利益分配。",
            "dimension": "T",
            "reverse_score": False,
            "category": "TF"
        },
        {
            "id": 32,
            "text": "在谈判中，我更关注共识和关系维护。",
            "dimension": "F",
            "reverse_score": False,
            "category": "TF"
        },
        {
            "id": 33,
            "text": "面对冲突，我会先分析是非对错。",
            "dimension": "T",
            "reverse_score": False,
            "category": "TF"
        },
        {
            "id": 34,
            "text": "面对冲突，我会先考虑如何缓和气氛。",
            "dimension": "F",
            "reverse_score": False,
            "category": "TF"
        },
        {
            "id": 35,
            "text": "我更容易被成就和完成任务所激励。",
            "dimension": "T",
            "reverse_score": False,
            "category": "TF"
        },
        {
            "id": 36,
            "text": "我更容易被欣赏和认可所激励。",
            "dimension": "F",
            "reverse_score": False,
            "category": "TF"
        },

        # 第四部分：生活方式 (J/P) - 37-48题
        {
            "id": 37,
            "text": "我喜欢制定计划并依计行事。",
            "dimension": "J",
            "reverse_score": False,
            "category": "JP"
        },
        {
            "id": 38,
            "text": "我喜欢灵活应变，保持开放选择。",
            "dimension": "P",
            "reverse_score": False,
            "category": "JP"
        },
        {
            "id": 39,
            "text": "我习惯有组织和有条理的生活方式。",
            "dimension": "J",
            "reverse_score": False,
            "category": "JP"
        },
        {
            "id": 40,
            "text": "我习惯随遇而安，灵活安排。",
            "dimension": "P",
            "reverse_score": False,
            "category": "JP"
        },
        {
            "id": 41,
            "text": "一旦定出计划，我会尽量遵守。",
            "dimension": "J",
            "reverse_score": False,
            "category": "JP"
        },
        {
            "id": 42,
            "text": "即使有计划，也喜欢探讨其他新方案。",
            "dimension": "P",
            "reverse_score": False,
            "category": "JP"
        },
        {
            "id": 43,
            "text": "我倾向于先工作后玩乐。",
            "dimension": "J",
            "reverse_score": False,
            "category": "JP"
        },
        {
            "id": 44,
            "text": "我倾向于工作时也会穿插放松。",
            "dimension": "P",
            "reverse_score": False,
            "category": "JP"
        },
        {
            "id": 45,
            "text": "我喜欢事情有明确的结论。",
            "dimension": "J",
            "reverse_score": False,
            "category": "JP"
        },
        {
            "id": 46,
            "text": "我喜欢过程比结果更重要。",
            "dimension": "P",
            "reverse_score": False,
            "category": "JP"
        },
        {
            "id": 47,
            "text": "我对截止日期有紧迫感，会提前完成。",
            "dimension": "J",
            "reverse_score": False,
            "category": "JP"
        },
        {
            "id": 48,
            "text": "我通常在截止日期前才能完成任务。",
            "dimension": "P",
            "reverse_score": True,  # 反向计分：高同意度表示P倾向
            "category": "JP"
        }
    ]

    return questions


def get_questions_by_category(category):
    """根据类别获取题目"""
    questions = get_all_questions()
    return [q for q in questions if q['category'] == category]


def validate_answer(answer):
    """验证单个答案的有效性"""
    if not isinstance(answer, dict):
        return False

    if 'question_id' not in answer or 'score' not in answer:
        return False

    if not isinstance(answer['question_id'], int):
        return False

    if not isinstance(answer['score'], int) or answer['score'] < -2 or answer['score'] > 2:
        return False

    return True