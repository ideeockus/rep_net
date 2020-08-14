import requests
import sys


#token = ""


def signup() -> dict:
    login = input("login ")
    email = input("email ")
    password = input("password ")
    """login = "radmirkaaa"
    email = "radmirka7456@gmail.com"
    password = "mysecretpass"""""
    signup_r = requests.post("http://127.0.0.1:8000/signup", params={'login': login, 'email': email, 'password': password})
    response = signup_r.json()
    print(response)
    print()

    if 'id' in response:
        user_id = response['id']
        return email_verification(login, user_id)
    elif 'error_code' in response:
        error_handler(response)
    else:
        print("error")
        signup()


def email_verification(login, user_id) -> dict:
    verification_code = input("Код подтверждения: ")
    signup_v = requests.post("http://127.0.0.1:8000/email_verification",  # send verification code
                             params={'login': login, 'user_id': user_id, 'verification_code': verification_code})
    response = signup_v.json()
    print(response)
    if 'token' in response:
        # token = response['token']
        return {'user_id': response['user_id'], 'token': response['token']}
    elif 'error_code' in response:
        error_handler(response)
    else:
        print("Ошибка")
        signup()


def signin() -> dict:
    login = input("login ")
    password = input("password ")
    signin_r = requests.post("http://127.0.0.1:8000/signin",
                             params={'login': login, 'password': password})
    response = signin_r.json()
    print(response)
    if 'token' in response:
        return {'user_id': response['user_id'], 'token': response['token']}
    elif 'error_code' in response:
        error_handler(response)
    else:
        print("Ошибка при авторизации")
        signin()


def error_handler(response):
    error_code = response['error_code']
    error_message = response['error']
    # print(error_message)
    e = {
        2: "Ваш аккаунт не подтвержден",
        3: "На этой почте уже зарегестрирован аккаунт",
        4: "К сожалению этот логин уже занят",
        5: "Код верификации неверен",
        6: "Данные для входа не верны",
        7: "На вашем балансе недостаточно средств",
        8: "Проверьте корректность ввода почты",
        9: "Неверный токен",
    }
    print(e[error_code])
    if error_code == 2:
        email_verification(response['login'], response['user_id'])


"""def get_id(token):
    get_id_r = requests.post("http://127.0.0.1:8000/get_id", params={'token': token})
    response = get_id_r.json()
    if 'user_id' in response:
        return response['user_id']
    else:
        print("id пользователя не определен")"""


def authorization():
    action = input("Signin or signup? ")
    if action == "signup":
        return signup()
    if action == "signin":
        return signin()


auth_data = authorization()
user_id = auth_data['user_id']
token = auth_data['token']
#user_id = get_id(token)
if not user_id:
    print("выхожу")
    sys.exit()
commands = ["journal", "balance", "transfer", "help"]
while(True):
    command = input(">")
    if command == "journal":
        journal_r = requests.post("http://127.0.0.1:8000/journal")
        response = journal_r.json()
        for user in response['journal']:
            print(str(user['id'])+" "+user['login']+" "+str(user['balance']))
        # print("journal: ")
        # print(response)
    if command == "balance":
        journal_r = requests.post("http://127.0.0.1:8000/get_balance", params={'user_id': user_id})
        response = journal_r.json()
        print("balance: ")
        print(response)
    if command == "transfer":
        dst_id = input("id адресата ")
        amount = input("количество ")
        journal_r = requests.post("http://127.0.0.1:8000/transfer",
                                  params={'src_id': user_id, 'dst_id': dst_id, 'rep_amount': amount, 'token': token})
        response = journal_r.json()
        print("ыыы")
        print(response)
    if command == "help":
        print(commands)
    else:
        if command not in commands:
            print("Unknown command")
