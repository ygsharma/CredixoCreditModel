

def additional_score(additional_variables):
    score = 0
    weights = {}

    cc_limit_check1 = additional_variables['cc_limit_check1']
    cc_limit_check2 = additional_variables['cc_limit_check2']
    cc_limit_check3 = additional_variables['cc_limit_check3']
    cc_limit_check4 = additional_variables['cc_limit_check4']
    cc_limit_check5 = additional_variables['cc_limit_check5']
    salary_check1 = additional_variables['salary_check1']
    salary_check2 = additional_variables['salary_check2']
    salary_check3 = additional_variables['salary_check3']
    salary_check4 = additional_variables['salary_check4']
    salary_check5 = additional_variables['salary_check5']
    premium_apps_check = additional_variables['premium_check']
    #name_msg_defaulter = additional_variables['name_msg_defaulter_check']


    if cc_limit_check1:
        score += 60
        weights['cc_limit'] = '+60'

    if cc_limit_check2:
        score += 50
        weights['cc_limit'] = '+50'

    if cc_limit_check3:
        score += 40
        weights['cc_limit'] = '+40'

    if cc_limit_check4:
        score += 30
        weights['cc_limit'] = '+30'

    if cc_limit_check5:
        score += 10
        weights['cc_limit'] = '+10'

    if salary_check1:
        score += 100
        weights['salary'] = '+100'

    if salary_check2:
        score += 80
        weights['salary'] = '+80'

    if salary_check3:
        score += 60
        weights['salary'] = '+60'

    if salary_check4:
        score += 40
        weights['salary'] = '+40'

    if salary_check5:
        score += 20
        weights['salary'] = '+20'

    if premium_apps_check:
        score += 50
        weights['premium_apps'] = '+50'

    # if name_msg_defaulter:
    #     score += 10
    #     weights['msg_default'] = '+10'

    return score, weights



