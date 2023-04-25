from flask import Flask, redirect, request, session, url_for, render_template
from urllib.parse import urlencode
import requests
import json

app = Flask(__name__)
app.secret_key = 'my_secret_key'

CLIENT_ID = '1098897625752805378'
CLIENT_SECRET = 'h5aOI2-Mdm_v-DBFE46eTi2uxEFB8mBs'
REDIRECT_URI = 'http://localhost:5000/callback'

@app.route('/')
def home():
    if 'user' in session:
        user = session['user']
        return render_template('home.html', user=user)
    else:
        return render_template('index.html')

@app.route('/login')
def login():
    # Создаем OAuth2 приложение в Discord Developer Portal и получаем CLIENT_ID и CLIENT_SECRET
    # Используем их для формирования ссылки на авторизацию
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': 'identify email',
    }
    return redirect(f'https://discord.com/api/oauth2/authorize?{urlencode(params)}')

@app.route('/callback')
def callback():
    # Получаем код авторизации из параметров запроса и обмениваем его на access_token
    code = request.args.get('code')
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'scope': 'identify email',
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
    token_data = json.loads(response.text)

    # Получаем информацию о пользователе, используя полученный access_token
    headers = {
        'Authorization': f'Bearer {token_data["access_token"]}'
    }
    response = requests.get('https://discord.com/api/users/@me', headers=headers)
    user_data = json.loads(response.text)

    # Сохраняем информацию о пользователе в сессию и перенаправляем на главную страницу
    session['user'] = {
        'id': user_data['id'],
        'username': user_data['username'],
        'discriminator': user_data['discriminator'],
        'avatar_url': f'https://cdn.discordapp.com/avatars/{user_data["id"]}/{user_data["avatar"]}.png',
        'email': user_data.get('email', None),
    }
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    # Удаляем информацию о пользователе из сессии и перенаправляем на главную страницу
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)