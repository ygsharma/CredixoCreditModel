from HardCode.scripts.Util import conn, convert_json, logger_1
import warnings
import re
from datetime import datetime
import pytz

warnings.filterwarnings("ignore")


def get_loan_closed_messages(data, loan_messages_filtered, result, name):
    logger = logger_1("loan closed messages", name)
    selected_rows = []
    all_patterns = [
        r'.*?loan.*?(?:closed|settled).*?',
        r'.*?closed.*?successfully.*?',
        r'successfully\sreceived\spayment.*rs\.\s[0-9]{3,6}',
        r'loan.*?paid\s(?:back|off)',
        r'making\spayment.*?home\scredit\sloan',
        r'bhugta+n\skarne\ske\sliye\sdhanya?wad',
        r'payment.*?(?:was|is)\ssuccessful',
        r'payment\sof.*?received.*?loan',
        r'payment\sof.*?agreement.*?received',
        r'received.*?payment\s(of|rs).*?loan',
        r'rcvd\spayment\s(of|rs).*?loan',
        r'thank\syou\sfor.*payment.*?towards.*?loan',
        r'acknowledge\sreceipt.*?emi\sof.*?(against|towards).*?loan',
        r'your\sfirst\sloan.*?paid\ssuccessfully',
        r'you\sjust\spaid.*?towards\sloan',
        r'thanks\sfor\spayment.*?for\sloan',
        r'payment\sreceived\sfor.*?loan',
        r'received.*\n\n.*towards\syour\sloan',
        r'(?:repayment|payment).*(?:is|has\sbeen)\s?(?:well)?\sreceived',
        r'received.*payment\sof\s(?:rs\.?|inr)',
        r'loan.*(?:paid|repaid)\ssuccessfully',
        r'received\syour\srepayment',
        r'loan.*already\s(?:is|has\sbeen)\srepaid',
        r'thanks\sfor.*repayment',
        r'due.*has been settled',
        r'thank.*for paying.*(?:loan|emi)',
        r'rs\.?\s?([0-9,]+[.]?[0-9]+)\sreceived',
        r'loan\shas\sbeen\spaid',
        r'received.*payment.*for.*?loan',
        r'emi.*?for\sthe\smonth\sof.*?received',
        r'repay\sbill\ssuccess',
        r'thank.*for\s?(?:your|making)?\spayment',
        r'payment.*?(?:was|is|has\sbeen)\ssuccessful'
    ]
    not_patterns = [r'waiver\sscheme',
                    r'loan\sextension\sdate|tenor\sextension',
                    r'seriously\soverdue',
                    r'haven\'t\spaid',
                    r'server\sissue']

    for i in range(data.shape[0]):
        if i not in loan_messages_filtered or 'payltr' in str(data['sender'][i]).lower():
            continue

        message = str(data['body'][i]).lower()
        for pattern in all_patterns:
            matcher = re.search(pattern, message)
            if matcher:
                match = False
                for pattern_2 in not_patterns:
                    matcher = re.search(pattern_2, message)
                    if matcher is not None:
                        match = True
                        break
                if match:
                    break
                selected_rows.append(i)
                break
    loan_messages_filter = list(set(loan_messages_filtered) - set(selected_rows))
    logger.info("Loan closed sms extracted successfully")

    logger.info("Append name in result dictionary for loan closed")
    if name in result.keys():
        a = result[name]
        a.extend(list(selected_rows))
        result[name] = a
    else:
        result[name] = list(selected_rows)
    logger.info("Appended name in result dictionary for loan closed successfully")

    mask = []
    for i in range(data.shape[0]):
        if i in selected_rows:
            mask.append(True)
        else:
            mask.append(False)
    logger.info("Dropped sms other than loan closed")
    x = data.copy()[mask].reset_index(drop=True)
    return x, loan_messages_filter


def replace_parenthesis(message):
    # this was done as in some cases cmount was written in a bracket due to which garbage value was detected by the
    # regex
    message = message.replace('(', '')
    message = message.replace(')', '')
    message = message.replace('*', '')
    message = message.replace('[','')
    message = message.replace(']','')
    return message


def get_loan_messages(data):
    loan_messages = []
    all_patterns = [
        ' loan ',
        'kreditbee',
        'cashbean',
        'loanfront',
        'loanapp',
        'kissht',
        'gotocash',
        'cashmama',
        'nira',
        'freeloan'
    ]
    header = ['kredtb', 'cashbn', 'lnfrnt', 'cshmma', 'kredtz', 'rrloan',
              'frloan', 'wfcash', 'bajajf', 'flasho', 'kissht', 'gtcash', 'bajafn', 'monvew', 'mpockt',
              'mpokkt', 'montap', 'mnytap', 'erupee', 'flasho', 'qcrdit', 'qcredt', 'cashln', 'paymei', 'pmifsp',
              'salary', 'esalry', 'cashme', 'moneed', 'bajajf', 'dhanii', 'idhani', 'dhanip', 'krbeee', 'krtbee',
              'nirafn', 'nlrafn', 'pdnira', 'pdnlra',
              'icredt', 'nanocd', 'nanocr', 'zestmn', 'loanzm', 'lnfrnt', 'loanap', 'cshmma', 'upward', 'loanit',
              'lenden', 'vivifi', 'shubln', 'paymin', 'homecr',
              'branch', 'sthfin', 'zestmn', 'loantp', 'mcreds', 'casheb', 'abcfin', 'cfloan', 'capflt', 'icashe',
              'loanxp', 'paysns', 'rapidr',
              'cbtest', 'rsloan', 'rupbus', 'ckcash', 'llnbro', 'cashbs', 'credme', 'atomec', 'finmtv', 'cashtm',
              'roboin', 'trubal', 'payltr', 'cashbk', 'loante',
              'payuib', 'iavail', 'smcoin', 'ruplnd', 'ftcash', 'rupeeh', 'cashmt', 'loanbl', 'cashep', 'cashem',
              'tatacp', 'loanco', 'loanfu', 'loanpl', 'haaloo',
              'rsfast', 'cashbo', 'cashin', 'rupmax', 'cashpd', 'lendko', 'loanfx', 'mudrak', 'prloan', 'cmntri',
              'cashmx', 'rupls', 'rscash', 'ezloan', 'ftloan','cashpy',
              'abcash', 'loanhr', 'ruplus', 'notice', 'uucash', 'gsimpl', 'kaarva', 'mnywow', 'zestmo', 'rupred',
              'mclick', 'cashwn', 'lzypay']
    ignore_header = ['kotakb', 'mafild', 'iiflfn', 'capflt', 'kotkbk', 'ktkbnk', 'fedbnk', 'icicib', 'obcbnk', 'empbnk',
                     'indbnk', 'qzhdfc', 'yesbnk', 'hdfcbn', 'kblbnk', 'hdfcbk', 'canbnk','idfcfb' , 'licind'
                     'synbnk', 'icicbk', 'hdfcpr', 'hdfcpll', 'icicbk', 'axisbk', 'kotakb', 'qlhdfc', 'vrhdfc',
                     'indusb']
    word1 = 'cashbean'
    word2 = 'zestmoney'
    data['body'] = data['body'].apply(lambda m: replace_parenthesis(m))

    for i in range(data.shape[0]):
        head = str(data['sender'][i]).lower()
        message = str(data['body'][i]).lower()
        p = True
        for j in ignore_header:
            if j in head:
                p = False
                break
        if not p:
            continue

        if re.search("[0-9]", head):

            if re.search(word1, message) and head[2] == "-":
                head = 'ab-cashbn'
            elif re.search(word2, message) and head[2] == "-":
                head = 'ab-zestmn'
            else:
                continue
        if head[2:] in header or head[3:] in header:
            loan_messages.append(i)
            continue
        else:
            for pattern in all_patterns:
                matcher = re.search(pattern, message)
                if matcher:
                    loan_messages.append(i)
                    break
    return loan_messages


def get_loan_messages_promotional_removed(data, loan_messages):
    loan_messages_filtered = []
    not_needed = []
    all_patterns = [
        r'kyc',
        r'sbi\scard',
        r'credited\sto\syour\swallet',
        r'spice\smoney',
        r'sign\sthe\selectronic\scontract',
        r'golden\slightning',
        r'gold\scash',
        r'after\syour\sconfirmation',
        r'your\spersonalised\sloan\soffer',
        r'emi\scard|credit\scard',
        r'\se-?sign\s',
        r'claim\sbonus',
        # r'icredit|rupeeplus',
        r'good\snews',
        r'confirm\snow',
        r'use\sdebit\scard.*netbanking.*wallets.*upi',
        r'are\syou\snot\sgetting\sloan',
        r'if\syou\shave.*overdue\sdebts',
        r'check\sthis\soffer',
        r'(?:extension|waiver|attractive|wow|dhamakedar|never\sbefore|believe\sit\sor\snot)\soffer',
        r'offer\sends',
        r'[0-9]+\s?day[s]?\sextension',
        r'limited\speriod\soffer',
        r'offering\sloan\sextension',
        r'get.*latest\supdates',
        r'gold\sloan'

    ]
    for i in range(data.shape[0]):
        if i not in loan_messages:
            continue
        message = str(data['body'][i]).lower()
        for pattern in all_patterns:
            matcher = re.search(pattern, message)
            if matcher:
                not_needed.append(i)
                break
    loan_messages_filtered = list(set(loan_messages) - set(not_needed))
    return loan_messages_filtered


def get_approval(data, loan_messages_filtered, result, name):
    logger = logger_1("loan approval", name)
    selected_rows = []
    all_patterns = [
        r'successfully\sapproved',
        r'has\sbeen\sapproved',
        r'documents\shas\sbeen\ssuccessfully\sverified',
        r'loan\syou\srequested\sis\sready\sfor\sdisbursal',
        r'is\sapproved',
        r'(?:is|was)\spassed',
        r'received\syour\sloan\saccount.*may\sreceive.*call'
    ]

    for i in range(data.shape[0]):
        if i not in loan_messages_filtered:
            continue
        message = str(data['body'][i]).lower()

        for pattern in all_patterns:
            matcher = re.search(pattern, message)
            if matcher:
                selected_rows.append(i)
                break
    loan_messages_filter = list(set(loan_messages_filtered) - set(selected_rows))
    logger.info("Loan approval sms extracted successfully")

    logger.info("Append name in result dictionary for loan approval")
    if name in result.keys():
        a = result[name]
        a.extend(list(selected_rows))
        result[name] = a
    else:
        result[name] = list(selected_rows)
    logger.info("Appended name in result dictionary for loan approval successfully")

    mask = []
    for i in range(data.shape[0]):
        if i in selected_rows:
            mask.append(True)
        else:
            mask.append(False)
    logger.info("Dropped sms other than loan approval")
    approve = data.copy()[mask].reset_index(drop=True)
    return approve, loan_messages_filter


def get_disbursed(data, loan_messages_filtered, result, name):
    logger = logger_1("loan disbursed", name)
    selected_rows = []
    all_patterns = [
        r'(?:is|has\sbeen)\s(?:disburse[d]?|credited)',
        r'disbursement\shas\sbeen\scredited',
        r'has\sbeen\stransferred.*account',
        r'disburse?ment.*has\sbeen\sinitiated',
        r'is\stransferred.*account',
        r'loan\sapplication.*?successfully\ssubmitted.*?bank',
        r'you.*?received.*?loan\samount',
        r'your.*?loan.*?made\ssuccessfully.*?loan\samount',
        r'loan\srs.*?disbursed',
        r'loan\shas\sbeen\sreleased\sto.*?bank',
        r'rs.*?credited\sto\sloan\sa\/c',
        r'disbursed.*?loan.*?to\syour\sbank',
        r'amount\sfinanced\sfor\sloan.*?rs',
        r'personal\sloan.*?transferred\ssuccessfully',
        r'your\sloan\sdisbursement\swas\ssuccess',
        r'loan.*?approved.*?cash.*?issued\sto.*?bank\saccount',
        r'loan.*?approved.*?will\stransfer.*?funds.*bank\saccount',
        r'loan.*approved.*fund[s]?\swill\sbe\stransferred.*bank\saccount',
        r'loan.*approved.*disbursed\sinto\syour\saccount',
        r'loan.*approved.*will\srelease.*loan\sto.*account',
        r'loan.*approved.*sent\srs.*to\syour\saccount',
        r'loan.*approved.*will\sbe\sdisbursed',
        r'loan.*approved.*credit\sto.*?bank\saccount',
        r'loan.*sent\sto\syour\sbank',
        r'sanctioned\syour\sloan',
        r'loan.*approved.*transferred.*account',
        r'loan.*rs.*[0-9] is\sprocessed\sfor\sdisbursal',
        r'transfer.*loan.*initiated',
        r'loan account.*credit.*rs.*[0-9]',
        r'credited.*amount\sto\s?(?:your)?\sbank',
        r'congratulations.*?credited\sfor\s(?:rs\.?|inr)',
        r'loan\sdisburse\smoney\ssuccess'
    ]
    not_patterns = [r'reward\s(?:of|point\sbalance)',
                    r'complete.*process',
                    r'click\sto\slogin',
                    r'through\s\'?digital\sshop',
                    r'\@upi',
                    r'received\spayment\sof',
                    r'you\swill\sbe\snotified\swhen\sthe\smoney\sis\sdisbursed',
                    r'your loan application.*has been successfully submitted']

    for i in range(data.shape[0]):
        if i not in loan_messages_filtered or 'payltr' in str(data['sender'][i]).lower():
            continue
        message = str(data['body'][i]).lower()
        for pattern in all_patterns:
            matcher = re.search(pattern, message)

            if matcher:
                match = False
                for pattern_2 in not_patterns:
                    matcher = re.search(pattern_2, message)
                    if matcher is not None:
                        match = True
                        break
                if match:
                    break
                selected_rows.append(i)
                break
    loan_messages_filter = list(set(loan_messages_filtered) - set(selected_rows))
    logger.info("Loan disbursed sms extracted successfully")

    logger.info("Append name in result dictionary for loan disbursed")
    if name in result.keys():
        a = result[name]
        a.extend(list(selected_rows))
        result[name] = a
    else:
        result[name] = list(selected_rows)
    logger.info("Appended name in result dictionary for loan disbursed successfully")

    mask = []
    for i in range(data.shape[0]):
        if i in selected_rows:
            mask.append(True)
        else:
            mask.append(False)
    logger.info("Dropped sms other than loan disbursed")
    z = data.copy()[mask].reset_index(drop=True)
    return z, loan_messages_filter


def get_loan_rejected_messages(data, loan_messages_filtered, result, name):
    logger = logger_1("loan rejection", name)
    selected_rows = []
    all_patterns_1 = [
        r'loan\sapplication.*?is\srejected',
        r'loan\sapplication.*?got\srejected',
        r'loan.*paysense\sis\srejected',
        r'has\sbeen.*?rejected',
        r'(?:is|was|has\sbeen|were)\s(?:declined|rejected)',
        r'has\sbeen\sdeclined',
        r'has\snot\sbeen\sapproved',
        r'was\snot\sapproved',
        r'was\sbeen\srejected',
        r'could\snot\sget\sapproved',
        r"sorry.*?couldn't.*?eligible.*?loan",
        r'credit.*rejected.*loan.*application'
        r'loan\s(?:is|was|has\sbeen)\srejected',
        r'sorry.*not.*suitable\sloan\soffer',
        r'unfortunately.*application\scould\snot\smatch.*eligibility\scriteria',
        r'sorry.*can\s?not\sprocess\syour\s?(?:loan)?\sapplication',
        r'loan\sprocess\scan\s?not\sbe\scompleted',
        r'loan\sapplication\shas\snot\spassed\sthe\sreview',
        r'(?:application|request)\s(?:can\s?not|could\snot)\sbe\sprocessed',
        r'loan\sapplication\sfailed\sto\spass',
        r'unable\sto\sserve\syou.*at\sthe\smoment',
        r'unfortunately.*can\s?not\sapprove\syou\sfor\s?[a]?\sloan',
        r'discrepancy\sin\sthe\sdocuments',
        r'unable\sto\sprocess\syour\sapplication',
        r'can\s?not\s(?:give|provide)\syou\s?[a]?\sloan',
        r'loan\sapplication.*(?:cancelled|rejected)',
        r'loan(.)*not(.)*eligib',
        r'loan\sdid\snot\spass',
        r"sorry.*(?:loan)?\sapplication.*(?:not|n't).*approved",
        r'application.*(?:cancelled|rejected)',
        r'not\sbe\sable\sto\sserve\syou',
        r'unfortunately.*not\squalify\sfor.*loan',
        r'loan.*not.*(?:approved|criteria)',
        r'unfortunately.*not\s(?:qualify|approve[d]?)\sfor.*loan',
        r'loan.*application\shas\sbeen\sdenied',
        r'could\snot\sapprove.*profile'
    ]
    all_patterns_2 = [
        r'low\scibil\sscore',
        r'low\scredit\sscore',
        r'is\sdue',
        r'network\scard'
    ]

    for i in range(data.shape[0]):
        if i not in loan_messages_filtered:
            continue
        message = str(data['body'][i]).lower()
        for pattern in all_patterns_1:
            matcher = re.search(pattern, message)
            if matcher:
                match = False
                for pattern_2 in all_patterns_2:
                    matcher = re.search(pattern_2, message)
                    if matcher is not None:
                        match = True
                        break
                if match:
                    break
                selected_rows.append(i)
                break

    loan_messages_filter = list(set(loan_messages_filtered) - set(selected_rows))
    logger.info("Loan rejection sms extracted successfully")

    logger.info("Append name in result dictionary for loan rejction")
    if name in result.keys():
        a = result[name]
        a.extend(list(selected_rows))
        result[name] = a
    else:
        result[name] = list(selected_rows)
    logger.info("Appended name in result dictionary for loan rejection successfully")

    mask = []
    for i in range(data.shape[0]):
        if i in selected_rows:
            mask.append(True)
        else:
            mask.append(False)
    logger.info("Dropped sms other than loan rejection")
    reject = data.copy()[mask].reset_index(drop=True)
    return reject, loan_messages_filter


def loan(args):
    df = args[0]
    result = args[1]
    user_id = args[2]
    max_timestamp = args[3]
    new = args[4]

    # logger = logger_1("loan_classifier", user_id)
    # logger.info("get all loan messages")
    # loan_messages = get_loan_messages(df)
    # logger.info("remove all loan promotional messages")
    # loan_messages_filtered = get_loan_messages_promotional_removed(df, loan_messages)
    #
    # logger.info("get all loan due overdue messages")
    # data = get_over_due(df, loan_messages_filtered, result, user_id)
    # logger.info("Converting loan due overdue dataframe into json")
    # data_over_due = convert_json(data, user_id, max_timestamp)
    #
    # logger.info("get all loan approval messages")
    # data = get_approval(df, loan_messages_filtered, result, user_id)
    # logger.info("Converting loan approval dataframe into json")
    # data_approve = convert_json(data, user_id, max_timestamp)
    #
    # logger.info("get all loan rejection messages")
    # data = get_loan_rejected_messages(df, loan_messages_filtered, result, user_id)
    # logger.info("Converting loan rejection dataframe into json")
    # data_reject = convert_json(data, user_id, max_timestamp)
    #
    # logger.info("get all loan disbursed messages")
    # data = get_disbursed(df, loan_messages_filtered, result, user_id)
    # logger.info("Converting loan disbursed dataframe into json")
    # data_disburse = convert_json(data, user_id, max_timestamp)
    #
    # logger.info("get all loan closed messages")
    # data = get_loan_closed_messages(df, loan_messages_filtered, result, user_id)
    # logger.info("Converting loan closed dataframe into json")
    # data_closed = convert_json(data, user_id, max_timestamp)

    logger = logger_1("loan_classifier", user_id)
    logger.info("get all loan messages")
    loan_messages = get_loan_messages(df)

    logger.info("remove all loan promotional messages")
    loan_messages_filtered = get_loan_messages_promotional_removed(df, loan_messages)
    logger.info("get all loan disbursed messages")

    data, loan_messages_filtered = get_disbursed(df, loan_messages_filtered, result, user_id)
    logger.info("Converting loan disbursed dataframe into json")
    data_disburse = convert_json(data, user_id, max_timestamp)

    logger.info("get all loan closed messages")
    data, loan_messages_filtered = get_loan_closed_messages(df, loan_messages_filtered, result, user_id)
    logger.info("Converting loan closed dataframe into json")
    data_closed = convert_json(data, user_id, max_timestamp)

    logger.info("get all loan due overdue messages")
    data, loan_messages_filtered = get_over_due(df, loan_messages_filtered, result, user_id)
    logger.info("Converting loan due overdue dataframe into json")
    data_over_due = convert_json(data, user_id, max_timestamp)

    logger.info("get all loan due messages")
    data, loan_messages_filtered = get_due_messages(df, loan_messages_filtered, result, user_id)
    logger.info("Converting loan due dataframe into json")
    data_due = convert_json(data, user_id, max_timestamp)

    logger.info("get all loan rejection messages")
    data, loan_messages_filtered = get_loan_rejected_messages(df, loan_messages_filtered, result, user_id)
    logger.info("Converting loan rejection dataframe into json")
    data_reject = convert_json(data, user_id, max_timestamp)

    logger.info("get all loan approval messages")
    data, loan_messages_filtered = get_approval(df, loan_messages_filtered, result, user_id)
    logger.info("Converting loan approval dataframe into json")
    data_approve = convert_json(data, user_id, max_timestamp)

    try:
        logger.info('making connection with db')
        client = conn()
        db = client.messagecluster
    except Exception as e:
        logger.critical('error in connection')
        return {'status': False, 'message': str(e), 'onhold': None, 'user_id': user_id, 'limit': None,
                'logic': 'BL0'}
    logger.info('connection success')

    if new:
        logger.info("New user checked")
        db.loanclosed.update({"cust_id": int(user_id)}, {"cust_id": int(user_id), 'timestamp': data_closed['timestamp'],
                                                         'modified_at': str(
                                                             datetime.now(pytz.timezone('Asia/Kolkata'))),
                                                         "sms": data_closed['sms']}, upsert=True)
        db.loanapproval.update({"cust_id": int(user_id)},
                               {"cust_id": int(user_id), 'timestamp': data_approve['timestamp'],
                                'modified_at': str(datetime.now(pytz.timezone('Asia/Kolkata'))),
                                "sms": data_approve['sms']}, upsert=True)
        db.loanrejection.update({"cust_id": int(user_id)},
                                {"cust_id": int(user_id), 'timestamp': data_reject['timestamp'],
                                 'modified_at': str(datetime.now(pytz.timezone('Asia/Kolkata'))),
                                 "sms": data_reject['sms']}, upsert=True)
        db.disbursed.update({"cust_id": int(user_id)},
                            {"cust_id": int(user_id), 'timestamp': data_disburse['timestamp'],
                             'modified_at': str(datetime.now(pytz.timezone('Asia/Kolkata'))),
                             "sms": data_disburse['sms']}, upsert=True)
        db.loanoverdue.update({"cust_id": int(user_id)},
                              {"cust_id": int(user_id), 'timestamp': data_over_due['timestamp'],
                               'modified_at': str(datetime.now(pytz.timezone('Asia/Kolkata'))),
                               "sms": data_over_due['sms']}, upsert=True)
        db.loandue.update({"cust_id": int(user_id)},
                          {"cust_id": int(user_id), 'timestamp': data_over_due['timestamp'],
                           'modified_at': str(datetime.now(pytz.timezone('Asia/Kolkata'))),
                           "sms": data_due['sms']}, upsert=True)
        logger.info("All loan messages of new user inserted successfully")
    else:

        for i in range(len(data_approve['sms'])):
            logger.info("Old User checked")
            db.loanapproval.update({"cust_id": int(user_id)}, {"$push": {"sms": data_approve['sms'][i]}})
            logger.info("loan approval sms of old user updated successfully")
        db.loanapproval.update_one({"cust_id": int(user_id)}, {
            "$set": {"timestamp": max_timestamp, 'modified_at': str(datetime.now(pytz.timezone('Asia/Kolkata')))}},
                                   upsert=True)
        logger.info("Timestamp of User updated")
        for i in range(len(data_reject['sms'])):
            logger.info("Old User checked")
            db.loanrejection.update({"cust_id": int(user_id)}, {"$push": {"sms": data_reject['sms'][i]}})
            logger.info("loan rejection sms of old user updated successfully")
        db.loanrejection.update_one({"cust_id": int(user_id)}, {
            "$set": {"timestamp": max_timestamp, 'modified_at': str(datetime.now(pytz.timezone('Asia/Kolkata')))}},
                                    upsert=True)
        logger.info("Timestamp of User updated")
        for i in range(len(data_disburse['sms'])):
            logger.info("Old User checked")
            db.disbursed.update({"cust_id": int(user_id)}, {"$push": {"sms": data_disburse['sms'][i]}})
            logger.info("loan disbursed sms of old user updated successfully")
        db.disbursed.update_one({"cust_id": int(user_id)}, {
            "$set": {"timestamp": max_timestamp, 'modified_at': str(datetime.now(pytz.timezone('Asia/Kolkata')))}},
                                upsert=True)
        logger.info("Timestamp of User updated")
        for i in range(len(data_over_due['sms'])):
            logger.info("Old User checked")
            db.loanoverdue.update({"cust_id": int(user_id)}, {"$push": {"sms": data_over_due['sms'][i]}})
            logger.info("loan due overdue sms of old user updated successfully")
        db.loanoverdue.update_one({"cust_id": int(user_id)}, {
            "$set": {"timestamp": max_timestamp, 'modified_at': str(datetime.now(pytz.timezone('Asia/Kolkata')))}},
                                  upsert=True)
        logger.info("Timestamp of User updated")
        for i in range(len(data_due['sms'])):
            logger.info("Old User checked")
            db.loandue.update({"cust_id": int(user_id)}, {"$push": {"sms": data_due['sms'][i]}})
            logger.info("loan due sms of old user updated successfully")
        db.loandue.update_one({"cust_id": int(user_id)}, {
            "$set": {"timestamp": max_timestamp, 'modified_at': str(datetime.now(pytz.timezone('Asia/Kolkata')))}},
                              upsert=True)
        logger.info("Timestamp of User updated")
        for i in range(len(data_closed['sms'])):
            logger.info("Old User checked")
            db.loanclosed.update({"cust_id": int(user_id)}, {"$push": {"sms": data_closed['sms'][i]}})
            logger.info("loan closed sms of old user updated successfully")
        db.loanclosed.update_one({"cust_id": int(user_id)}, {
            "$set": {"timestamp": max_timestamp, 'modified_at': str(datetime.now(pytz.timezone('Asia/Kolkata')))}},
                                 upsert=True)
        logger.info("Timestamp of User updated")
    client.close()
    return {'status': True, 'result': result}


def get_due_messages(data, loan_messages_filtered, result, name):
    selected_rows = []
    all_patterns = [
        r'is\sdue',
        r'loan\sis\sdue',
        r'due\sdate',
        r'due\shai',
        r'loan\sis\son\sdue',
        r'loan.*?emi\srs.*?due\son',
        r'repay\syour\semi\samount\sdue\son',
        r'loan.*?borrowed.*?will\sbe\sdue\son',
        r'k[io]\sdey\shai',
        r'pay.*?loan\sof\srs.*?by',
        r'your\srepayment\sdate.*?repayment\samount',
        r'loan.*?bakaya\shai',
        r'earlysalary.*?requested\spayment',
        r'emi.*?dhani\sloan\sis\sstill\sdue',
        r'last\sday\sfor.*?loan\srepayment',
        r'do\snot\sforget\sto\spay.*?loan',
        r'emi.*?will\sbe\s(auto-)?debited',
        r'dues\sof\srs.*?outstanding.*?for\sloan',
        r'payment.*rs\.?.*?([0-9]+).*due',
        r'due.*on\s([0-9]+-[0-9]+?-[0-9]+).*payment.*rs\.?\s?([0-9]+)',
        r'rs\.?\s([0-9]+).*due.*([0-9]+-[0-9]+-[0-9]+)',
        r'due\s(?:on)?.*([0-9]+/[0-9]+)',
        r'loan.*rs\.?.*?([0-9]+).*due',
        r'payment.*\sdue',
        r'(?:emi|loan|repayment|payment)\sis\sdue',
        r'is\syour\sdue\s(?:day|date)',
        r'(?:a\/c|account)\sis\sdue',
        r'repayment\sdue\s(?:day|date)',
        r'will\sbe\sauto\s?[-]?debited.*against\syour\sdues',
        r'make.*repayment.*immediately.*avoid\supheaval',
        r'remind\s?\s?you.*loan.*due\ssoon',
        r'repayment\sdate\sis',
        r'loan\sis\spending',
        r'emi\swill\sbe\sdeducted.*keep\ssufficient\sbalance',
        r'emi\swill\sbecome\sdue\son',
        r'loan\semi\sis\sdue',
        r'repay\syour.*emi\searly',
        r'(?:loan|emi).*due\s(?:on\s|is\s|)(?:tomorrow|today)',
        r'loan\sto\sbe\srepaid',
        r'(?:loan\sre[-]?payment|instal[l]?ment).*is\sdue',
        r'emi.*is\sdue',
        r'emi\srepayment\sdate',
        r'will\s?(?:be)?\sdue',
        r'(?:today|tomorrow).*(?:due|repayment)\s(?:date|day)',
        r'due\sby\s(?:tomorrow|today)',
        r'due\sis\scoming\sup'
    ]

    for i in range(data.shape[0]):
        if i not in loan_messages_filtered or 'payltr' in str(data['sender'][i]).lower():
            continue
        message = str(data['body'][i]).lower()
        for pattern in all_patterns:
            matcher = re.search(pattern, message)
            matcher1 = re.search('extend.*due\sdate', message)
            if matcher and not matcher1:
                selected_rows.append(i)
                break

    loan_messages_filter = list(set(loan_messages_filtered) - set(selected_rows))
    if name in result.keys():
        a = result[name]
        a.extend(list(selected_rows))
        result[name] = a
    else:
        result[name] = list(selected_rows)

    mask = []
    for i in range(data.shape[0]):
        if i in selected_rows:
            mask.append(True)
        else:
            mask.append(False)
    due = data.copy()[mask].reset_index(drop=True)
    return due, loan_messages_filter


def get_over_due(data, loan_messages_filtered, result, name):
    logger = logger_1("loan due overdue", name)
    selected_rows = []
    # pattern_1 = r'(.*)?immediate(.*)payment(.*)'
    # pattern_2 = r'(.*)?delinquent(.*)?'
    # # pattern_3 = r'(.*)?has(.*)cd?bounced(.*)?'
    # pattern_4 = r'missed(.*)?payments'
    # pattern_5 = r'(.*)?due(.*)?'
    # pattern_6 = r'\sover-?due\
    all_patterns = [
        r'missed.*installment.*pay\sback',
        r'immediate\spayment',
        r'delinquent',
        r'missed\spayments',
        r'is\soverdue',
        r'overdue\shai',
        r'\sover-?due',
        r'emi\sof.*?was\sdue\son',
        r'payment\sof.*?against.*?loan.*?bounced',
        r"you\sstill\shaven['o]t\spaid.*?loan",
        r'you\shave\smissed.*?payment.*?loan',
        r'charges\sof\srs.*?in\syour\sloan',
        r'not\spaid\semi.*?against\syour\sloan',
        r'payment\sis\sdelayed\sby\sweeks',
        r'your\sloan\sis\sstill\sunpaid',
        r'promised\sto\spay\srs.*?loan',
        r'instalment\sis\sunpaid',
        r'.*loan.*overdue.*repayable\sis\srs.\s?([0-9]+)',
        r'.*loan.*rs\.\s([0-9]+).*overdue.*',
        r'.*loan.*overdue.*repayment.*rs\.?\s([0-9]+)',
        r'despite\sseveral\sreminders.*over[-]?\s?due.*legal\saction',
        r'not\sreceived\s(?:outstanding|o\/s)\s(?:amount|amt)',
        r'loan\srepayment\sis\slate',
        r'not\s(?:make|made).*payment\sof.*loan\swithin.*due\sdate',
        r'overdue\sbills\shave\snot\sbeen\sprocessed',
        r'loan.*passed\sthe\sdue\sdate',
        r'repayment.*is\spending',
        r'settle\syour\sdues.*legal\saction',
        r'[^a-z\-]pay\s(?:immediately|urgently|now)',
        r'(?:loan|emi|payment).*over\s?[-]?due',
        r'loan.*successfully\srescheduled',
        r'[^a-z]payment.*(?:yet|still)?not\s?(?:yet|still)?.*received',
        r'loan.*din\sse\szyada\sdue',
        r'over[_]?due\sfor\s([0-9]+)\sdays',
        r'payment.*not\sdone.*many\sdays',
        r'not\sreceive[d]?.*amount.*avoid\slegal\saction',
        r'emi.*due.*(?:has\sbeen|is)\sbounce[d]?',
        r'overdue.*make.*payment\simmediately.*avoid.*(?:penalt[y]?[i]?[e]?[s]?|charges)',
        r'failed\sto\ssettle.*outstanding\sdue[s]?',
        r'not\sdone.*payment\syet.*not\sresponding.*kindly\spay',
        r'despite.*reminder[s]?.*(?:still)\snot\sreceived',
        r'still\sunpaid.*reported',
        r'not\spaid.*sent\slegal\snotice',
        r'pay\sback.*to\sensure.*delay\sdpd\sis\snot\supdate[d]?',
        r'amount\sis\sover\s?due',
        r'rs\.?\s([0-9,]+[.]?[0-9]+)\shas\sbeen\sover\s?due',
        r'we\swill\sbe\sshortly\sreporting\sto\scibil',
        r'outstanding\sof\srs\.?.*is\sover[_]?due',
        r'payment.*overdue\s(?:since|from)',
        r'more\sthan.*days\soverdue',
        r'overdue\spayment\snotice',
        r'overdue\s(?:by|since|for|from)\s[0-9]+\s?day[s]?',
        r'[0-9]+\s?day[s]?\spast.*due\sdate',
        r'this\sis\sa\sreminder\smessage.*keep\scalling\syour\semergency\scontact',
        r'payment.*not\smade.*negative\scustomer',
        r'not\sa\ssingle\spayment.*made.*outstanding\sloan'
    ]
    not_patterns = [r'(?:to|is)\sdue',
                    r'(?:0|-1)\s?day[s]?\soverdue',
                    r'(?:penalties|charges).*waived',
                    r'fee\swill\sbe\s(?:reduced|reducted)',
                    r'will\s(?:be|cause)\s(?:due|overdue)',
                    r'technical\s(?:issue|error)',
                    r'top(\-?\s?)up|cashback',
                    r'(?:extended|extension).*loan.*(?:date|tenure)',
                    r'loan.*rescheduled',
                    r'click\sto\s(?:login|download)',
                    r'credit\sscore.*pay.*loan.*pay\snow',
                    r'coupon.*penalty.*if.*overdue',
                    r'repayment.*next\sloan.*do\snot\soverdue',
                    r'to\sstop\slegal.*pay\snow',
                    r'reach.*us.*get.*flexible\spayment\soption',
                    r'make.*payment.*avoid.*overdue',
                    r'overdue\swill.*affect.*credit',
                    r'overdue\swill\scause.*charges',
                    r'(?:today|tomorrow).*(?:due|repayment)\s(?:date|day)',
                    r'extended.* due\sdate',
                    r'loan.*overdue\stoday',
                    r'last\sday\sto\savoid.*overdue',
                    r'due\s(?:date\day).*tomorrow',
                    r'last\stime.*got\sextra\sdays\sto\srepay',
                    r'emi.*due.*tomorrow']

    for i in range(data.shape[0]):
        if i not in loan_messages_filtered:
            continue
        message = str(data['body'][i]).lower()
        for pattern in all_patterns:
            matcher = re.search(pattern, message)
            if matcher:
                match = False
                for pattern_2 in not_patterns:
                    matcher = re.search(pattern_2, message)
                    if matcher is not None:
                        match = True
                        break
                if match:
                    break
                selected_rows.append(i)
                break
    loan_messages_filter = list(set(loan_messages_filtered) - set(selected_rows))
    logger.info("Loan due overdue sms extracted successfully")
    logger.info("Append name in result dictionary for loan due overdue")
    if name in result.keys():
        a = result[name]
        a.extend(list(selected_rows))
        result[name] = a
    else:
        result[name] = list(selected_rows)
    logger.info("Appended name in result dictionary for loan due overdue successfully")

    mask = []
    for i in range(data.shape[0]):
        if i in selected_rows:
            mask.append(True)
        else:
            mask.append(False)
    logger.info("Dropped sms other than loan due overdue")
    overdue = data.copy()[mask].reset_index(drop=True)
    return overdue, loan_messages_filter
