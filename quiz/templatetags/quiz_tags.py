from django import template

register = template.Library()


# @register.inclusion_tag('correct_answer.html', takes_context=True)
# def answers_correct(context, ques):
#     """
#     processes the correct answer based on a given question object
#     if the answer is incorrect, informs the user
#     """
#     question_answers = ques.get_choices()
#     questions_incorrect_list = context.get('incorrect_questions', [])
#     if ques.id in questions_incorrect_list:
#         user_was_incorrect = True
#     else:
#         user_was_incorrect = False
#
#     return {'previous': {'answers': question_answers},
#             'user_was_incorrect': user_was_incorrect}

@register.inclusion_tag('correct_answer.html', takes_context=True)
def answers_correct(context, ques):
    """
    Processes the correct answer based on a given question object.
    If the answer is incorrect, informs the user.
    """
    if hasattr(ques, 'get_choices'):
        question_answers = ques.get_choices()
    else:
        question_answers = []

    questions_incorrect_list = context.get('incorrect_questions', [])
    if ques.id in questions_incorrect_list:
        user_was_incorrect = True
    else:
        user_was_incorrect = False

    return {'previous': {'answers': question_answers},
            'user_was_incorrect': user_was_incorrect}


@register.filter
def answer_choice_to_string(q, a):
    return q.answer_choice_to_string(a)
