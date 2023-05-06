from datetime import datetime, date
from HardCode.scripts.Util import conn
import pytz


def secure_unsecured_loan(cibil_df):
    """
    :param  cibil_df
    :returns the count of secured and unsecured loans calculated from the cibil dataframe
    :rtype: dict
    """
    secured_loan = 0
    unsecured_loan = 0
    if cibil_df:
        if cibil_df['data'] is not None:  # ==>> this check is added cause in case cibil file is not uploaded
            if not cibil_df['data'].empty:  # ==> dataframe is returned as None instead of an empty df
                secured_loan = int(cibil_df['data']['secured_loan'].iloc[-1])
                unsecured_loan = int(cibil_df['data']['unsecured_loan'].iloc[-1])
    return secured_loan,unsecured_loan
