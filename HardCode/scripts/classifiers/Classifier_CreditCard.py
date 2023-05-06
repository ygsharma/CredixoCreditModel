import re
from HardCode.scripts.Util import conn, convert_json, logger_1
import warnings
from datetime import datetime
import pytz

warnings.filterwarnings("ignore")


def get_confirm_cc_messages(data):
    cc_confirm_index_list = []
    all_patterns = [
        r'cardholder.*payment.*rs\.?\s?([0-9.?]+).*credit\scard.*successfully',
        # r'approve\stransaction.*rs\.?\s?([0-9.?]+).*a/c\sno\.?.*credit\scard',
        r'(?:rs|inr)\.?\s?\s?([0-9,]+[.]?[0-9]+).*debited.*(?:available|avbl).*(?:limit|lmt\.?).*(?:rs\.?|inr)\s?([0-9,]+[.]?[0-9]+)',
        r'(?:rs|inr)\.?\s?\s?([0-9,]+[.]?[0-9]+).*(?:debited|deposited)',
        r'inr\s?([0-9.?]+).*paytm.*credit\scard',
        r'(?:txn|transaction|payment)\sof\s(?:inr|rs\.?)\s?([0-9.?]+).*credit\scard',
        r'refund.*(?:rs\.?|inr)\s?([0-9.?]+).*credited.*credit\scard',
        r'spent\s(?:rs\.?|inr)\s?([0-9.?]+).*credit\scard',
        r'payment.*(?:(?:(?:[Rr][sS]|inr)\.?\s?)(\d+(:?\,\d+)?(\,\d+)?(\.\d{1,2})?)).*(?:received|successful|expired|unsuccessful)',
        r'payment.*(?:rs\.?|inr)\s?\s?([0-9,]+[.]?[0-9]+).*successfully\sprocessed',
        r'received.*payment.*(?:for|of)*(?:rs\.?|inr)\s?([0-9.?]+).*credit\scard',
        r'(?:(?:(?:[Rr][sS]|inr)\.?\s?)(\d+(:?\,\d+)?(\,\d+)?(\.\d{1,2})?)).*(?:spent|credited).*credit\scard',
        r'.*charge\sof\s(?:rs\.?|inr)\s?([0-9.?]+).*initiated.*credit\scard.*',
        r'.*internet\spayment.*(?:rs\.?|inr)\s?([0-9.,?]+).*credit\scard.*',
        r'(?:e-)?stmt.*credit[\s]?card.*due',
        r'payment.*credit\scard.*is\sdue.*total\samount\s(?:due|overdue:).*(?:rs|\s)\.?\s?([0-9.?]+).*minimum\samount\s(?:due|due:).*(?:rs|\s)\.?\s?([0-9.?]+)',
        r'stmt.*total\s(?:amt|amount)\sdue.*credit\scard.*(?:inr|rs\.?)\s?([0-9.,?]+).*(?:minimum|min)\s(?:amt|amount)\sdue.*(?:inr|rs\.?)\s?([0-9.,?]+).*payable',
        r'(?:statement|stmt).*credit\scard.*total\s(?:amount|amt).*(?:rs\.?|inr)\s?([0-9.,?]+).*min'
        r'(?:amount|amt|payment).*(?:rs\.?|inr)\s?([0-9.,?]+).*due',
        r'total\samount\sdue.*credit\scard.*(?:rs\.?|inr)\s?([0-9.,?]+).*',
        r'payment.*credit\scard.*due.*(?:minimum|min).*rs\.?\s?\s?([0-9.,?]+).*total.*rs\.?\s?\s?([0-9.,?]+)',
        r'forward.*receiving\s?rs\.?\s?([0-9.,?]+).*credit\scard',
        r'credit\scard.*payment.*rs\.?\s?([0-9.,?]+).*due.*min.*rs\.?\s?([0-9.,?]+)',
        r'credit\scard.*(?:statement|stmt).*rs\.?\s?([0-9.,?]+).*due.*min.*rs\.?\s?([0-9.,?]+)',
        r'payment.*credit\scard.*due.*(?:minimum|min).*rs\.?\s?([0-9]+[.,]?).*',
        r'not\sreceived\spayment.*credit\scard.*rs\.?\s?([0-9]+)',
        r'necessary.*payment.*rs\.?\s?([0-9]+[.,]?).*credit\scard',
        r'credit\scard\sdues.*unpaid.*rs\.?\s?([0-9]+[.,]?)',
        r'received.*payment.*(?:rs\.?|inr)\s?([0-9,]+[.]?[0-9]+).*(?:available|avl\.?).*(?:limit|lmt\.?).*(rs\.?|inr)\s?([0-9,]+[.]?[0-9]+)',
        r'unable.*overdue\s(?:payment|pymt).*rs\.?\s?([0-9.?]+).*credit\scard',
        r'payment.*overdue.*credit\scard.*(?:pl|please|pls)\spay.*total\s(?:amt|amount).*due.*(?:rs\.?|inr)\s?([0-9.,?]+).*min.*(?:amt|amount).*(?:rs\.?|inr)\s?([0-9.,?]+)',
        r'overdue\samount.*(?:rs\.?|inr)\s?([0-9.,?]+).*credit\scard',
        r'payment.*credit\scard.*is\s(due|overdue).*total\samount\s(?:due|overdue:|outstanding).*(?:rs)\.?\s?\s?([0-9.?]+).*minimum\samount\s(?:due|due:).*(?:rs)\.?\s?\s?([0-9.?]+)',
        r'account.*rs\.?\s?([0-9.,?]+).*overdue.*credit\scard',
        r'credit\scard.*rs\.?\s?\s?([0-9.,?]+).*overdue.*minimum.*(?:due|payment).*rs\.?\s?\s?([0-9.,?]+)',
        r'repeated\sreminders.*credit\scard.*overdue.*pay\.?\s?\s?([0-9]+[.,]?).*immediately',
        r'regret\sto\sinform.*unable\sto\s(?:issue|sanction).*credit\scard',
        r'application.*credit\scard[s]?.*(?:reject[e]?[d]?|declined)',
        r'regret\sto\sinform.*review[e]?[d]?.*application.*unable\sto\sgrant.*credit\scard',
        r'txn.*credit\scard.*(?:rs\.?|inr)\s?([0-9.?]+).*(?:declined|approved)',
        r'(?:transaction|trxn|txn).*credit\scard.*(?:rs\.?|inr)\s?([0-9.?]+).*not\sapprove[d]?',
        r'(?:txn|trxn).*rs\.?\s?([0-9.,?]+).*(?:credit\scard|card).*declined',
        r'credit\scard.*blocked.*total.*rs\.?\s?([0-9.,?]+).*minimum.*rs\.?\s?([0-9.,?]+)',
        r'credit\scard.*blocked.*immediate',
        r'request\sto\sincrease.*credit\slimit.*initiated',
        # r'convert.*(?:transaction|trxn|txn)\sof\s(?:rs\.?|inr)\s?([0-9]+[.]?[0-9]+).*into.*emi[s]?',
        # r'transfer.*outstanding\scredit\scard.*personal\sloan',
        r'(?:sbidrcard|sbi\s?card).*used\sfor\s(?:rs\.?|inr)\s?([0-9,]+[.][0-9]+)',
        r'fund\stransfer\spayment.*towards.*credit\scard',
        r'(?:(?:(?:[Rr][sS]|inr)\.?\s?)(\d+(:?\,\d+)?(\,\d+)?(\.\d{1,2})?)).*credited\sto.*credit\scard',
        r'(?:(?:(?:[Rr][sS]|inr)\.?\s?)(\d+(:?\,\d+)?(\,\d+)?(\.\d{1,2})?)).*is\soverdue\son.*credit\scard',
        r'regret\sto\sinform.*credit\scard.*not.*approved',
        r'payment[s]?\son.*credit\scard.*(?:are|is)\soverdue',
        r'credited.*amount.*credit\scard',
        r'(?:(?:(?:[Rr][sS]|inr)\.?\s?)(\d+(:?\,\d+)?(\,\d+)?(\.\d{1,2})?)).*due.*payment.*credit\scard',
        r'credit\scard.*unpaid.*overdue.*(?:(?:(?:[Rr][sS]|inr)\.?\s?)(\d+(:?\,\d+)?(\,\d+)?(\.\d{1,2})?))',
        r'credit\sof.*(?:(?:(?:[Rr][sS]|inr)\.?\s?)(\d+(:?\,\d+)?(\,\d+)?(\.\d{1,2})?)).*credit\scard',
        r'credit\scard.*due.*min\sdue.*(?:(?:(?:[Rr][sS]|inr)\.?\s?)(\d+(:?\,\d+)?(\,\d+)?(\.\d{1,2})?))',
        # r'credit\scard.*upgraded',
        r'payment.*sufficient\sfunds.*credit\scard',
        r'(?:(?:(?:[Rr][sS]|inr)\.?\s?)(\d+(:?\,\d+)?(\,\d+)?(\.\d{1,2})?)).*credit\scard.*sufficient\sfunds',
        r'debited.*(?:(?:(?:[Rr][sS]|inr)\.?\s?)(\d+(:?\,\d+)?(\,\d+)?(\.\d{1,2})?)).*payment\sof.*credit[\s]?card',
        r'payment.*(?:(?:(?:[Rr][sS]|inr)\.?\s?)(\d+(:?\,\d+)?(\,\d+)?(\.\d{1,2})?)).*credited\sto.*card',
        r'accepted.*request.*moratorium.*credit\scard',
        r'amount.*(?:(?:(?:[Rr][sS]|inr)\.?\s?)(\d+(:?\,\d+)?(\,\d+)?(\.\d{1,2})?)).*due.*credit\scard',
        r'credit\scard.*enrolled.*moratorium',
        r'charges\sreversal.*(?:(?:(?:[Rr][sS]|inr)\.?\s?)(\d+(:?\,\d+)?(\,\d+)?(\.\d{1,2})?)).*credit\scard',
        r'bill.*credit\scard.*sent',
        r'(?:txn|trxn|transaction).*done\son\scard',
        r'withdrawn\sfrom\sa\/c.*\sat\s.*\satm\s?\.',
        r'credited\swith.*credit\scard',
        r'alert.*due.*card.*(?:(?:(?:[Rr][sS]|inr)\.?\s?)(\d+(:?\,\d+)?(\,\d+)?(\.\d{1,2})?))',
        r'debited\swith.*credit[\s]?card',
        #abhishek
        r'approve[d]?\s(?:inr\.?|rs\.?).*card',
        r'(?:transaction|trxn|txn).*card.*for\s(inr\.?|rs\.?).*(?:successful|credited|reversed)',
        r'paid.*using.*credit\scard',
        r'stmt.*(?:credit\s?card|sbi\scard).*sent',
        r'credit\scard.*successfully\sregistered.*payment\sdeferment',
        r'payment.*(?:received|processed|credited).*(?:credit\s?card|card)',
        r'credit\scardholder.*outstanding\son\syour\scard',
        r'no\spayment.*required.*statement.*credit\s?card.*payment\sdeferment',
        r'convert\soutstanding.*credit\scard.*into\semi',
        r'(?:credit\scard|).*moratorium\s(?:will\send|enabled).*(?:credit\s?card|card|)',
        r'(?:transaction|trxn|txn).*card.*(?:successful|credited|reversed|declined)',
        r'payment.*credit\scard.*(?:successful|due|overdue)',
        r'(?:credit\scard|card|).*(?:statement|stmt).*(?:credit\scard|card|)generated',
        r'attempt[s]?\sto\sresolve.*overdue.*unsuccessful',
        r'stmt.*credit\s?card.*bounce[d]?',
        r'payment.*credit\s?card.*not.*executed',
        r'(?:available|avl\.?)\s(?:limit|lmt\.?).*(?:credit\s?card|card)',
        r'killed\syour\sbill.*credit\scard',
        r'exceeded.*credit\slimit.*credit\scard',
        r'transaction\sof.*converted\s(?:into|to)\semi',
        r'transaction.*credit\scard.*qualifies\sfor\semi\sconversion',
        r'spent.*card.*auth\scode'
    ]

    not_patterns = [r'reward\spoint',r'otp',
                    r'incorrect\scvv',r'debit\scard|debitcard',
                    r'sbidrcard', r'debit\/atm card']

    cc_list = []
    credit_card_pattern_1 = "credit card|creditcard|credit crd"
    credit_card_pattern_2 = "sbi card|sbicard"
    credit_card_pattern_3 = "rbl supercard"
    credit_card_pattern_4 = 'sbi cardholder'
    credit_card_pattern_5 = 'hdfcbank cardmember'
    credit_card_pattern_6 = '\scard\s(no\.?\s)?[?\*nx\s]+([0-9]{4,})'
    credit_card_pattern_7 = '\scard\sending\s([0-9]{4,})'
    for i in range(data.shape[0]):
        message = str(data['body'][i]).lower()
        matcher_1 = re.search(credit_card_pattern_1, message)
        matcher_2 = re.search(credit_card_pattern_2, message)
        matcher_3 = re.search(credit_card_pattern_3, message)
        matcher_4 = re.search(credit_card_pattern_4, message)
        matcher_5 = re.search(credit_card_pattern_5, message)
        matcher_6 = re.search(credit_card_pattern_6, message)
        matcher_7 = re.search(credit_card_pattern_7, message)
        if matcher_1 or matcher_2 or matcher_3 or matcher_4 or matcher_5 or matcher_6 or matcher_7:
            cc_list.append(i)
    for i in range(data.shape[0]):
        if i in cc_list:
            for pattern in all_patterns:
                message = str(data['body'][i]).lower()
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
                    cc_confirm_index_list.append(i)
                    break
    return cc_confirm_index_list


def credit(args):
    df = args[0]
    result = args[1]
    user_id = args[2]
    max_timestamp = args[3]
    new = args[4]

    logger = logger_1("credit card", user_id)
    # logger.info("Removing credit card promotional sms")
    # data_not_needed = get_creditcard_promotion(df)
    logger.info("Extracting Credit card sms")
    data_needed = get_confirm_cc_messages(df)
    if user_id in result.keys():
        a = result[user_id]
        a.extend(list(data_needed))
        result[user_id] = a
    else:
        result[user_id] = list(data_needed)
    mask_needed = []
    for i in range(df.shape[0]):
        if i in data_needed:
            mask_needed.append(True)
        else:
            mask_needed.append(False)
    data = df.copy()[mask_needed].reset_index(drop=True)
    logger.info("Converting credit card dataframe into json")
    data_credit = convert_json(data, user_id, max_timestamp)

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
        # db.creditcard.insert_one(data_credit)
        db.creditcard.update({"cust_id": int(user_id)}, {"cust_id": int(user_id), "sms": data_credit['sms'],
                                                         'modified_at': str(
                                                             datetime.now(pytz.timezone('Asia/Kolkata'))),
                                                         "timestamp": data_credit['timestamp']}, upsert=True)
        logger.info("Credit card sms of new user inserted successfully")
    else:
        for i in range(len(data_credit['sms'])):
            logger.info("Old User checked")
            db.creditcard.update({"cust_id": int(user_id)}, {"$push": {"sms": data_credit['sms'][i]}})
            logger.info("Credit card sms of old user updated successfully")
        db.creditcard.update_one({"cust_id": int(user_id)}, {
            "$set": {"timestamp": max_timestamp, 'modified_at': str(datetime.now(pytz.timezone('Asia/Kolkata')))}},
                                 upsert=True)
        logger.info("Timestamp of User updated")
    client.close()
    return {'status': True, 'result': result}
