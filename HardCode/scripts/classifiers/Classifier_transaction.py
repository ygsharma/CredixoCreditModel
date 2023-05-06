import re
from datetime import datetime
import pytz
import threading
from HardCode.scripts.Util import conn, convert_json, logger_1
import warnings

warnings.filterwarnings("ignore")

def check_account_number(message):
    all_patterns = [
    r'[\*nx]+([0-9]{3,})',
    r'[a]\/c ([0-9]+)',
    r'[\.]{3,}([0-9]+)',
    r'account(.*)?\[([0-9]+)\]'
    ]

    for pat in all_patterns:
        matcher = re.search(pat, message)    
        if matcher:
            return True
    return False

def cleaning(args):
    df = args[0]
    result = args[1]
    user_id = args[2]
    max_timestamp = args[3]
    new = args[4]

    logger = logger_1("cleaning", user_id)
    transaction_patterns = ['debited', 'credited', "inft"]

    required_rows = []
    internet_banking = []
    spcl_salary = []
    withdraw = []
    avail = []
    pattern_inb_wd = [" inb txn ", "w/d@", "w/d at"]
    for index, row in df.iterrows():
        body = row["body"].lower()
        sender = row["sender"].lower()[3:]
        if sender in ['cbsbnk','dopbnk','csisms','cbssbi']:
            if ' credit ' in body:
                spcl_salary.append(index)
                continue
        match = True
        for pattern in transaction_patterns:
            matcher = re.search(pattern, body)
            if matcher:
                required_rows.append(index)
                match = False
                break
        with_match = False
        if match:
            for pat in pattern_inb_wd:
                matcher = re.search(pat, body)
                if matcher:
                    internet_banking.append(index)
                    with_match = True
                    break
        if match and with_match:
            matcher = re.search("withdraw", body)
            if matcher:
                if check_account_number(body):
                    withdraw.append(index)
        if re.search('\savail\sbal.*cr\s',body):
            avail.append(index)


    cleaning_transaction_patterns_header = ['vfcare',
                                            'oyorms',
                                            'payzap',
                                            'rummy',
                                            'polbaz',
                                            'rummyc',
                                            'rupmax',
                                            'ftcash',
                                            'dishtv',
                                            'bigbzr',
                                            'olamny',
                                            'bigbkt',
                                            'olacab',
                                            'urclap',
                                            'ubclap',
                                            'qeedda',
                                            'myfynd',
                                            'cmntri',
                                            'gofynd',
                                            'paytm',
                                            'airbnk',
                                            'phonpe',
                                            'paysns',
                                            'fabhtl',
                                            'spcmak',
                                            'cuemth',
                                            'rechrg',
                                            'zestmn',
                                            'pcmcmh',
                                            'dlhvry',
                                            'bludrt',
                                            'airtel',
                                            'acttvi',
                                            'erecharge',
                                            'swiggy',
                                            'fpanda',
                                            'simpl',
                                            'mytsky',
                                            'vodafone',
                                            'sydost',
                                            'ipmall',
                                            'quikrr',
                                            'mututc',
                                            'muthut',
                                            'mytsky',
                                            'lenkrt',
                                            'epfoho',
                                            'flpkrt',
                                            'flasho',
                                            'grofrs',
                                            'hdfcsl',
                                            'idhani',
                                            'adapkr',
                                            'ipmall',
                                            'oxymny',
                                            'jionet',
                                            'kissht',
                                            'kredtb',
                                            'shoekn',
                                            'lzypay',
                                            'mobikw',
                                            'mdlife',
                                            'notice',
                                            'payltr',
                                            'salary',
                                            'swiggy',
                                            'vishal',
                                            'qira',
                                            'domino',
                                            'dinout',
                                            'quikrd',
                                            'goibib',
                                            'cureft',
                                            'olacbs',
                                            'ryatri',
                                            'dhanip',
                                            'zestmo',
                                            'smart',
                                            'myntra',
                                            'reings',
                                            'reingp',
                                            'monybk']
    garbage_header_rows = []
    for i, row in df.iterrows():
        if i in required_rows:
            for pattern in cleaning_transaction_patterns_header:
                if pattern in row["sender"].lower():
                    garbage_header_rows.append(i)
                    break

    required_rows = list(set(required_rows) - set(garbage_header_rows))
    g = []
    for index, row in df.iterrows():
        if index not in required_rows:
            continue
        matcher_1 = re.search("[Rr]egards", row["body"])
        matcher_2 = re.search(r"\d", row["sender"])
        if matcher_1 is not None:
            if 'DHANCO' not in row["sender"]:
                g.append(index)
        elif matcher_2 is not None:
            g.append(index)

    required_rows = list(set(required_rows) - set(g))

    cleaning_transaction_patterns = ['request received to', 'received a request to add', 'premium receipt',
                                     'contribution',
                                     'data benefit', 'team hr', 'free [0-9]+ ?[gm]b', ' data ', 'voucher', 'data pack',
                                     'benefit of ', 'data setting', 'added/ ?modified a beneficiary',
                                     'added to your beneficiary list', 'after activation', 'new beneficiary',
                                     'refund credited', 'return request', 'received request',
                                     'documents have been received',
                                     'last day free', 'received a refund', 'will be processed shortly',
                                     'credited a free',
                                     'request for modifying', r'free \d+ [gm]b/day', 'data pack',
                                     'request for registration',
                                     'received by our company', 'month of', 'received a call', 'free data', 'welcome',
                                     'data benefits', 'win real cash',
                                     'received full benefit', 'payment against', 'auto debited', 'mandates',
                                     'we apologize for the incorrect sms',
                                     'coupon', 'can be credited ', 'no hassle of adding beneficiary', 'you\'re covered',
                                     'bank will never ask you to', 'eAadhaar', 'great news!', 'your query has',
                                     'redemption request', 'number received',
                                     'your order', 'beneficiary [a-z]+? is added successfully', 'dear employee',
                                     'subscribing', 'sorry',
                                     r'received \d*? enquiry', 'congratulations?', 'woohoo!', 'salary credited',
                                     'hurry',
                                     'sign up', 'credited to your wallet', 'safe & secure!', '[gm]b is credited on',
                                     'cash reward',
                                     'remaining emi installment', 'salary amount', 'incentive amount ', 'dear investor',
                                     'verification code', 'outstanding dues', 'congrat(ulation)?s', 'available limit ',
                                     'oyo money credited',
                                     'reminder', 'card ?((holder)|(member))', 'login request', 'cashback',
                                     'electricity bill', 'data pack activation',
                                     'paytm postpaid bill', 'failed', 'declined', 'cardmember', 'credit ?card',
                                     ' porting ', 'lenskart',
                                     'activated for fund transfer', 'biocon', 'updated wallet balance', 'recharging',
                                     'assessment year', 'we wish to inform', 'refunded',
                                     'amendment', 'added/modified', 'kyc verification', 'is due', 'paytm postpaid',
                                     'please pay', 'flight booking', 'offer',
                                     '(credited)?(received)? [0-9]+[gm]b', 'payment.*failed',
                                     'uber india systems pvt ltd', 'has requested money', 'on approving',
                                     'not received', 'received your', 'brand factory has credited ', 'train ticket',
                                     'total (amt)?(amount)? due', 'redbus wallet', '\notp\n',
                                     'due of', 'received ?a? ?bill', 'successful payments', 'response ', 'last day',
                                     'payment confirmation', 'payment sms', 'kyc',
                                     'added beneficiary', 'received a message', ' premium ', 'claim', 'points ',
                                     'frequency monthly', 'received a pay rise', 'cheque book',
                                     'will be', 'unpaid', 'received (for|in) clearing', 'presented for clearing',
                                     'your application', 'to know', 'unpaid', r'\slakh\s', 'thanking you', 'redeem',
                                     'transferred',
                                     'available credit limit']

    garbage_rows = []
    for i, row in df.iterrows():
        if i in required_rows:
            message = row["body"].lower()
            for pattern in cleaning_transaction_patterns:
                matcher = re.search(pattern, message)
                if matcher:
                    garbage_rows.append(i)
                    break

    required_rows = list(set(required_rows) - set(garbage_rows))

    loan_messages = []
    for i, row in df.iterrows():
        if i not in required_rows:
            continue
        matcher = re.search("loan", row['body'].lower())
        if matcher is not None:
            loan_messages.append(i)
    imp_loan_messages = []
    pattern_0 = 'info.*?loan'
    pattern_1 = r'[\*nx]+([0-9]{3,})'
    pattern_2 = r'[a]\/c ([0-9]+)'
    pattern_3 = r'[\.]{3,}([0-9]+)'
    pattern_4 = r'account\s?[\*nx]+([0-9]{3,})'
    pattern_unmatch = r'loan (a\/c|account)'

    for i, row in df.iterrows():
        if i not in loan_messages:
            continue
        message = row['body'].lower()
        matcher_1 = re.search(pattern_1, message)
        matcher_2 = re.search(pattern_2, message)
        matcher_3 = re.search(pattern_3, message)
        matcher_4 = re.search(pattern_4, message)
        matcher_0 = re.search(pattern_0, message)
        matcher_unmatch = re.search(pattern_unmatch, message)
        if matcher_0 is not None:
            imp_loan_messages.append(i)

        elif matcher_1 is not None:
            if matcher_unmatch is None:
                imp_loan_messages.append(i)

        elif matcher_2 is not None:
            if matcher_unmatch is None:
                imp_loan_messages.append(i)

        elif matcher_3 is not None:
            if matcher_unmatch is None:
                imp_loan_messages.append(i)

        elif matcher_4 is not None:
            if matcher_unmatch is None:
                imp_loan_messages.append(i)
    required_rows = list(set(required_rows) - set(loan_messages))
    required_rows.extend(list(set(imp_loan_messages)))
    logger.info("important loan messages saved")
    required_rows.extend(internet_banking)
    required_rows.extend(withdraw)
    required_rows.extend(spcl_salary)
    required_rows.extend(avail)
    if user_id in result.keys():
        a = result[user_id]
        a.extend(list(required_rows))
        result[user_id] = a
    else:
        result[user_id] = list(required_rows)
    logger.info("Appended name in result dictionary for transaction messages successfully")

    mask = []
    for i in range(df.shape[0]):
        if i in required_rows:
            mask.append(True)
        else:
            mask.append(False)
    df_transaction = df.copy()[mask]
    df_transaction = df_transaction.reset_index(drop=True)
    logger.info("Dropped sms other than transaction")
    logger.info("Converting transaction messages dataframe into json")
    data_transaction = convert_json(df_transaction, user_id, max_timestamp)

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
        # db.transaction.insert_one(data_transaction)
        db.transaction.update({"cust_id": int(user_id)}, {"cust_id": int(user_id), 'sms': data_transaction['sms'],
                                                          'modified_at': str(
                                                              datetime.now(pytz.timezone('Asia/Kolkata'))),
                                                          "timestamp": data_transaction['timestamp']}, upsert=True)
        logger.info("All transaction messages of new user inserted successfully")
    else:
        for i in range(len(data_transaction['sms'])):
            logger.info("Old User checked")
            db.transaction.update({"cust_id": int(user_id)}, {"$push": {'sms': data_transaction['sms'][i]}})
            logger.info("transaction sms of old user updated successfully")
        db.transaction.update_one({"cust_id": int(user_id)}, {
            "$set": {"timestamp": max_timestamp, 'modified_at': str(datetime.now(pytz.timezone('Asia/Kolkata')))}},
                                  upsert=True)
        logger.info("Timestamp of User updated")
    client.close()
    return {'status': True, 'result': result}
