import requests


#token = ""


def signup() -> str:
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


def email_verification(login, user_id):
    verification_code = input("Код подтверждения: ")
    signup_v = requests.post("http://127.0.0.1:8000/email_verification",  # send verification code
                             params={'login': login, 'user_id': user_id, 'verification_code': verification_code})
    response = signup_v.json()
    print(response)
    if 'token' in response:
        # token = response['token']
        return response['token']
    elif 'error_code' in response:
        error_handler(response)
    else:
        print("Ошибка")
        signup()


def signin() -> str:
    login = input("login ")
    password = input("password ")
    signin_r = requests.post("http://127.0.0.1:8000/signin",
                             params={'login': login, 'password': password})
    response = signin_r.json()
    print(response)
    if 'token' in response:
        return response['token']
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
    }
    print(e[error_code])
    if error_code == 2:
        email_verification(response['login'], response['user_id'])


action = input("Signin or signup? ")
if action == "signup":
    signup()
if action == "signin":
    signin()


