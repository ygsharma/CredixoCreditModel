from HardCode.scripts.Util import conn
import itertools
from HardCode.scripts.parameters_for_bl0.available_balance.available_balance import find_info


def mean_available(user_id):
    connect = conn()
    mean_bal = -1
    avg_bal = -1
    third_last_month = {}
    scnd_last_month = {}
    last_month = {}
    data = connect.analysis.balance_sheet.find_one({'cust_id':user_id})

    if not data:
        return mean_bal,last_month,scnd_last_month,third_last_month,avg_bal
    data = data['sheet']
    avbl = find_info(user_id)
    ac_no = avbl['AC_NO']
    avbl_bal = []
    if ac_no:
        for i in range(len(data)):
            acn = str(data[i]['acc_no'])[-3:]
            if acn == str(ac_no):
                avbl_bal.append(data[i])
    avbl_bal.sort(key=lambda x: x['timestamp'])
    dfs = []
    key = lambda datum: datum['timestamp'].rsplit('-', 1)[0]

    for key, group in itertools.groupby(avbl_bal, key):
        dfs.append({'time': key, 'data': list(group)})

    all_max_bal = []
    all_max_time = []
    all_max_msg = []
    monthly_avg_bal = []
    dfs = dfs[-3:]

    for i in range(len(dfs)):
        list_bal = []
        list_time = []
        list_msg = []

        for j in range(len(dfs[i]['data'])):
            if int(dfs[i]['data'][j]['Available Balance']) > 0:
                list_bal.append(int(dfs[i]['data'][j]['Available Balance']))
                list_time.append(dfs[i]['data'][j]['timestamp'])
                list_msg.append(dfs[i]['data'][j]['body'])
        if list_bal:
            monthly_avg_bal.append(sum(list_bal)/len(list_bal))
            maxpos = list_bal.index(max(list_bal))
            all_max_bal.append(max(list_bal))
            all_max_time.append(list_time[maxpos])
            all_max_msg.append(list_msg[maxpos])

    if all_max_bal:
        mean_bal = round(sum(all_max_bal) / len(all_max_bal),2)

    if monthly_avg_bal:
        avg_bal = round(sum(monthly_avg_bal)/len(monthly_avg_bal),2)
    try:
        third_last_month = {'max_amt':all_max_bal[-3],'datetime':all_max_time[-3],'msg':all_max_msg[-3]}
    except:
        third_last_month = {}
    try:
        scnd_last_month = {'max_amt': all_max_bal[-2], 'datetime': all_max_time[-2], 'msg': all_max_msg[-2]}
    except:
        scnd_last_month = {}
    try:
        last_month = {'max_amt': all_max_bal[-1], 'datetime': all_max_time[-1], 'msg': all_max_msg[-1]}
    except:
        last_month = {}


    return mean_bal,last_month,scnd_last_month,third_last_month,avg_bal

