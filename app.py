from flask import Flask, request, jsonify
from werkzeug.routing import Rule
from werkzeug.exceptions import HTTPException
import json, requests

app = Flask(__name__)
app.url_rule_class = lambda rule, **kwargs: Rule(rule, **{**kwargs, 'methods': None})

def login(user, password):
    response = requests.post(
        'https://dash.cloudflare.com/api/v4/login',
        json.dumps({'email': user, 'password': password}),
        headers={'Content-Type': 'application/json'}
    )
    if response.json()['success'] != True: raise Exception('login.failed')
    return response.cookies

@app.route('/client/v4/<path:path>')
def client(path):
    response = requests.request(
        request.method,
        f'https://dash.cloudflare.com/api/v4/{path}',
        data=request.get_data(),
        cookies=login(request.headers.get('X-Auth-Email'), request.headers.get('X-Auth-Key'))
    )
    return response.content, response.status_code, [
        (key, value) for key, value in response.raw.headers.items()
        if key.lower() not in ['accept-ranges', 'connection', 'content-encoding', 'content-length', 'keep-alive', 'proxy-authenticate', 'proxy-authorization', 'te', 'trailers', 'transfer-encoding', 'upgrade']
    ]

@app.errorhandler(Exception)
def handler(error):
    return jsonify({
        'success': False,
        'errors': [{'code': 114514, 'message': error.name if isinstance(error, HTTPException) else error.args[0] if len(error.args) > 0 else 'Unknown error'}],
        'messages': [],
        'result': None
    })

if __name__ == '__main__':
    app.run()
