import json
import os
from datetime import datetime
from time import sleep
import shutil
import pytz
from HardCode.scripts import BL0
from HardCode.scripts.update_analysis import update
from HardCode.scripts.analysis_n_parameters import analysis_n_parameters
from HardCode.scripts.Util import conn
# from HardCode.scripts.cibil.apicreditdata import convert_to_df
from analysisnode.settings import PROCESSING_DOCS, CHECKSUM_KEY, FINAL_RESULT, DEBUG
from concurrent.futures import ProcessPoolExecutor
from analysisnode import Checksum
import requests
import pandas as pd


def parallel_proccess_user_records(user_id_dir):
    step = int(user_id_dir[-1])
    user_id = user_id_dir[:-2]
    # cibil_df = {'status': False, 'data': None, 'message': 'None'}
    # if os.path.exists(PROCESSING_DOCS + str(user_id) + '/experian_cibil.xml'):
    #     response_parser = convert_to_df(open(PROCESSING_DOCS + str(user_id) + '/experian_cibil.xml'))
    #     cibil_df = response_parser
    try:
        sms_json = json.load(open(PROCESSING_DOCS + str(user_id_dir) + '/sms_data.json', 'rb'))
        # try:
        #     old_sms = open(f'../../old_users/{user_id}/sms_data.json', 'rb')
        #     old_sms_json = json.load(old_sms)
        #     sms_json.update(old_sms_json)
        #     old_sms.close()
        # except Exception as e:
        #     print(str(e))

        if len(sms_json) == 0:
            final_response = {
                "status": True,
                "cust_id": user_id,
                "message": "No messages found in sms_json",
                "result": False
            }
            if step == 0:
                final_response["result_type"] = "update_analysis"
            elif step == 1:
                final_response["result_type"] = "before_kyc"
            elif step == 2:
                final_response["result_type"] = "before_cibil"
            elif step == 3:
                final_response["result_type"] = "before_loan"
        else:
            # UPDATE ANALYSIS
            if step == 0:
                resonse = update(user_id=user_id, sms_json=sms_json)
                if resonse['status']:
                    final_response = {"status": True,
                                      "cust_id": user_id,
                                      "result": True,
                                      "result_type": "update_analysis"}
            # KYC STEP
            elif step == 1:
                contact_csv = pd.read_csv(f"{PROCESSING_DOCS}/{user_id}_1/contacts.csv", header=None, index_col=0,
                                          squeeze=True).to_dict()
                with open(f"{PROCESSING_DOCS}/{user_id}_1/app_data.json") as f:
                    app_data = json.load(f)
                with open(f"{PROCESSING_DOCS}/{user_id}_1/profile_data.json") as f:
                    profile_data = json.load(f)
                response = analysis_n_parameters(user_id=int(user_id), sms_json=sms_json, contacts=contact_csv,
                                                 app_data=app_data, profile_info=profile_data)
                print(response)
                if response['status']:
                    response['result_type'] = 'before_kyc'
                    final_response = response
                else:
                    final_response = {"status": False,
                                      "cust_id": user_id,
                                      "result": False,
                                      "result_type": "before_kyc"}
            # CIBIL STEP
            elif step == 2:
                # before cibil
                pass
            # LOAN STEP
            elif step == 3:
                response = BL0.bl0(user_id=user_id, sms_json=sms_json)
                if response['status']:
                    final_response = response
                else:
                    final_response = {"status": False,
                                      "cust_id": user_id,
                                      "result": False,
                                      "result_type": "before_loan"}

            # response_bl0 = BL0.bl0(cibil_xml=cibil_df, cibil_score=user_data['cibil_score'], user_id=int(user_id)
            #                        , new_user=user_data['new_user'], list_loans=user_data['all_loan_amount'],
            #                        current_loan=user_data['current_loan_amount'], sms_json=sms_json)
        shutil.rmtree(PROCESSING_DOCS + str(user_id_dir))

    except Exception as e:
        print(f"error in middleware {e}")
        final_response = {
            "cust_id": user_id,
            "status": False,
            "message": str(e),
            "result": False
        }
        if step == 0:
            final_response["result_type"] = "update_analysis"
        elif step == 1:
            final_response["result_type"] = "before_kyc"
        elif step == 2:
            final_response["result_type"] = "before_cibil"
        elif step == 3:
            final_response["result_type"] = "before_loan"
        try:
            shutil.move(PROCESSING_DOCS + str(user_id_dir), "error_docs/")
        except:
            shutil.rmtree(PROCESSING_DOCS + str(user_id_dir))
    final_response['modified_at'] = str(datetime.now(pytz.timezone('Asia/Kolkata')))
    temp_response_bl0 = final_response
    del temp_response_bl0["cust_id"]
    conn().analysisresult.bl0.update_one({'cust_id': int(user_id)}, {"$push": {
        "result": temp_response_bl0}}, upsert=True)
    final_response['user_id'] = int(user_id)


def process_user_records(user_ids):
    with ProcessPoolExecutor() as p:
        p.map(parallel_proccess_user_records, user_ids)


if __name__ == "__main__":
    while True:
        no_of_dirs = len(os.listdir(PROCESSING_DOCS))
        if no_of_dirs > 0:
            directories = os.listdir(PROCESSING_DOCS)
            user_ids = [user_id for user_id in directories]
            process_user_records(user_ids)
            print("***********")
            print("Done : ")
            print(user_ids)
        print("SLEEPING.....zzzzzz")
        sleep(5)
