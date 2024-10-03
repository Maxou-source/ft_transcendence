import requests

USER_42_INFO_URL = 'https://api.intra.42.fr/v2/me'

def get_user_info(token):
    response = requests.get(USER_42_INFO_URL, headers={
        'Authorization': f'Bearer {token}'
    })
    if (response.status_code == 200):
        data = response.json()
        return {
            'ok': True,
            'user': data
        }
    return {
        'ok': False,
        'user': {}
    }

def get_user_info_from_session(session):
    return {
        'id': session['user']['id'],
        'url': session['user']['url'],
        'login': session['user']['login'],
        'email': session['user']['email'],
        'image': session['user']['image'],
        'wallet': session['user']['wallet'],
        'location': session['location'],
        'pool_year': session['user']['pool_year'],
        'last_name': session['user']['last_name'],
        'first_name': session['user']['first_name'],
    }