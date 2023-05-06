import json
import os
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from analysisnode.Checksum import verify_checksum
from analysisnode.settings import CHECKSUM_KEY, PROCESSING_DOCS


@api_view(['POST'])
@permission_classes((AllowAny,))
def get_cibil_analysis(request):
    print(request.data)
    try:
        if not verify_checksum({'user_id': int(request.data.get('user_id'))}, CHECKSUM_KEY, request.headers['CHECKSUMHASH']):
            raise ValueError
    except (AttributeError, ValueError, KeyError):
        return Response({'error': 'INVALID CHECKSUM!!!'}, 400)
    try:
        user_id = int(request.data.get('user_id'))
    except:
        return Response({'status': False, 'message': 'user_id parameter is required'}, 400)
    try:
        new_user = request.data.get('new_user', '1')
        if new_user is None:
            raise Exception
        new_user = bool(int(new_user))
    except:
        pass
    try:
        step = int(request.data.get('step'))
    except:
        return Response({'status': False, 'message': 'step parameter is required'}, 400)
    try:
        sms_json = request.FILES['sms_json']
        try:
            os.makedirs(PROCESSING_DOCS + str(user_id))
        except FileExistsError:
            pass
        with open(PROCESSING_DOCS + str(user_id) + '/sms_data.json', 'wb+') as destination:
            for chunk in sms_json.chunks():
                destination.write(chunk)

        if sms_json is None:
            raise Exception

    except TypeError:
        return Response({'status': False, 'message': 'sms_json parameter is required'}, 400)

    try:
        cibil_xml = request.FILES['cibil_xml']
        with open(PROCESSING_DOCS + str(user_id) + '/experian_cibil.xml', 'wb+') as destination:
            for chunk in cibil_xml.chunks():
                destination.write(chunk)
    except:
        pass

    try:
        cibil_score = request.data.get('cibil_score', 600)
        if cibil_score is None:
            raise Exception
    except:
        pass
    try:
        current_loan_amount = request.data.get('current_loan_amount', 0)
        if current_loan_amount is None:
            raise Exception
    except:
        pass

    try:
        all_loan_amount = request.data.get('all_loan_amount', '1000,2000,3000,4000')
        if all_loan_amount is None:
            raise Exception
    except:
        pass
    try:
        contacts = request.FILES['contacts']
        with open(PROCESSING_DOCS + str(user_id) + '/contacts.csv', 'wb+') as destination:
            for chunk in contacts.chunks():
                destination.write(chunk)
    except:
        pass
    try:
        app_data = request.data.get('app_data')
    except:
        pass
    # call parser
    try:
        all_loan_amount = list(map(lambda x: int(float(x)), all_loan_amount.split(',')))
    except:
        pass

    try:
        current_loan_amount = int(current_loan_amount)
    except:
        pass
    with open(PROCESSING_DOCS + str(user_id) + '/user_data.json', 'w') as json_file:
        json.dump({
            'current_loan_amount': current_loan_amount,
            'all_loan_amount': all_loan_amount,
            'cibil_score': cibil_score,
            'user_id': user_id,
            'new_user': new_user,
            'step': step
        }, json_file, ensure_ascii=True, indent=4)
        # return Response({'status': False, 'message': 'current_loan_amount parameter must be int convertible'}, 400)
    return Response({'message': 'FILES RECEIVED!!'})
