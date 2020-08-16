from fastapi import FastAPI
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean
from sqlalchemy.sql import select
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import hashlib
import secrets


def send_mail(destination_mail, mail_subject, mail_text):
    smtp_bot = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_bot.starttls()
    smtp_bot.login('radmirka.tech.mail@gmail.com', '@TechnicalMailPass7210')

    msg_from = "RadmirkaTech"
    msg_to = [destination_mail]

    email_text = MIMEText(mail_text, 'plain', 'utf-8')
    email_text['Subject'] = Header(mail_subject, 'utf-8')
    email_text['From'] = msg_from
    email_text['To'] = destination_mail
    smtp_bot.sendmail(msg_from, msg_to, email_text.as_string())
    print("Email sent")
    print(email_text)
    smtp_bot.quit()


def password_sha256_hash(password: str) -> str:
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return password_hash


engine = create_engine('sqlite:///rep_net.db')
#engine = create_engine('postgresql+psycopg2://tqaqqwpktjeovm:7250b55f8604b7126e5d8e826b0222abbf7f77d4979cb476f9ca85ff742510d0@ec2-54-247-118-139.eu-west-1.compute.amazonaws.com/d8sl82suln18cs')
engine_connection = engine.connect()
meta = MetaData()

accounts_db = Table(
    'accounts_1', meta,
    Column('id', Integer, primary_key=True),
    Column('login', String),  # name
    Column('email', String),  # email
    Column('password', String),  # password hash
    Column('balance', Integer),  # balance
    Column('token', String),  # token
    Column('verification_code', String),  # temp (for verifications)
    Column('email_verification_status', Boolean),  # email verification status
)
meta.create_all(engine)

app = FastAPI()


@app.get("/signup")
@app.post("/signup")
async def signup(login: str, email: str, password: str):  # sign up
    print("signup request has gotten")

    if (not login.strip()) or (not password.strip()) or (not email.strip()):
        print("no enough information")
        return {'error': "Не все поля заполнены", 'error_code': 1}

    password_hash = password_sha256_hash(password+login)
    verification_code = secrets.token_hex(3)

    print("looking for login "+login+" in database...")
    registered_logins = engine.execute(select([accounts_db.c.login])).fetchall()
    if (login,) in registered_logins:  # login check
        print("login is busy")
        return {'error': "Логин уже занят", 'error_code': 4}  # error codes for better?
    print("login OK")

    print("looking for email "+email+" in database...")
    registered_emails = engine.execute(select([accounts_db.c.email])).fetchall()
    if (email,) in registered_emails:  # email check
        return("email is busy")
        return {'error': "На эту почту уже зарегистрирована учетная запись", 'error_code': 3}  # error codes for better?
    print("email OK")
    print("try to send verification code...")
    try:  # try to send email with code
        send_mail(email, "Код верификации", f"Привет, {login}\nВаш код верификации: {verification_code}")
    except smtplib.SMTPRecipientsRefused:  # if email invalid
        print("invalid email")
        return {'error': "invalid email", 'error_code': 8}
    print("Verification code sended")
    print("creating new record in database...")
    new_acc_insert = accounts_db.insert().values(login=login, email=email,  # new user creation
                                                 password=password_hash, balance=1000,
                                                 verification_code=verification_code,
                                                 email_verification_status=False
                                                 )
    result = engine_connection.execute(new_acc_insert)
    account_id = result.inserted_primary_key
    print("databse record created")
    print(f"new id {account_id}")
    return {'login': login, 'email': email, 'status': "ok", 'user_id': account_id[0]}


@app.post("/email_verification")
async def email_verification(login: str, user_id: int, verification_code: str):
    print("email verification request has gotten")
    if (not login.strip()) or (not str(user_id).strip()) or (not verification_code.strip()):
        print("no enough information")
        return {'error': "Не все поля заполнены", 'error_code': 1}

    print("request parameters:")
    print(login, user_id, verification_code)
    db_veref_code = engine_connection.execute(select([accounts_db.c.verification_code])  # local verif code
                                              .where(accounts_db.c.id == user_id)).fetchone()[0]

    token = secrets.token_urlsafe(32)  # token generation

    print("verification code validation...")
    if verification_code == db_veref_code:  # comparasion with verif code in request
        engine_connection.execute(accounts_db.update()
                                  .where(accounts_db.c.id == user_id)
                                  .values(email_verification_status=True, token=token, verification_code=""))
        print("validation OK")
        return {'status': "ok", 'user_id': user_id, 'message': "verification successful", 'token': token}
    else:
        print("validation ERROR")
        return {'user_id': user_id, 'error': "wrong code", 'error_code': 5}


@app.get("/signin")
@app.post("/signin")
async def signin(login: str, password: str):
    print("signin request has gotten")
    if (not login.strip()) or (not password.strip()):
        print("no enough information")
        return {'error': "Не все поля заполнены", 'error_code': 1}

    password_hash = password_sha256_hash(password+login)

    print("authorization")
    try:
        engine_connection.execute(select([accounts_db.c.id])
                                  .where(accounts_db.c.login == login)
                                  .where(accounts_db.c.password == password_hash)).fetchone()[0]
    except TypeError:
        print("authorization ERROR")
        return {'error': "Ошибка авторизации", 'error_code': 6}
    print("authorization OK")

    # I guess that there can be only one record with such login:password pair
    user_id = engine.execute(select([accounts_db.c.id])
                                        .where(accounts_db.c.login == login)
                                        .where(accounts_db.c.password == password_hash)).fetchone()[0]

    # Check if this account is unverified
    user_email_verification = engine.execute(select([accounts_db.c.email_verification_status])
                                                        .where(accounts_db.c.id == user_id)).fetchone()[0]
    if not user_email_verification:
        print("account is not verified")
        return {'error': "Аккаунт не подтвержден", 'login': login, 'user_id': user_id, 'error_code': 2}

    token = secrets.token_urlsafe(32)
    engine.execute(accounts_db.update().where(accounts_db.c.id==user_id).values(token=token))
    return {'user_id': user_id, 'token': token}


def get_id(token: str):
    # I guess that there can be only one record with such token
    user_id = engine.execute(select([accounts_db.c.id]).where(accounts_db.c.token==token)).fetchone()[0]
    print(user_id)
    if user_id:
        return {'user_id': user_id}
    else:
        return {'error': "ошибка"}


@app.post("/journal")
def get_all_accounts():
    journal = engine.execute(select([accounts_db.c.login, accounts_db.c.balance, accounts_db.c.id])).fetchall()
    return {'journal': journal}


@app.post("/get_balance")
def get_balance(user_id: int):
    user_balance = engine.execute(select([accounts_db.c.balance]).where(accounts_db.c.id == user_id)).fetchone()[0]
    return {'user_id': user_id, 'balance': user_balance}


@app.post("/transfer")
def transfer(src_id: int, dst_id: int, rep_amount: int, token: str):

    if src_id==dst_id:
        return {'error': "self transaction not allowed", 'error_code': 9}
    if rep_amount<0:
        return {'error': "wrong amount value", 'error_code': 9}

    get_id_req = get_id(token)
    if not ('user_id' in get_id_req):
        return get_id_req
    token_owner_id = get_id_req['user_id']
    if not (token_owner_id == src_id):
        print("SRC_ID:"+str(src_id))
        print("TOKEN OWNER ID"+str(token_owner_id))
        return {'error': "wrong token", 'error_code': 9}

    src_balance = get_balance(src_id)['balance']
    dst_balance = get_balance(dst_id)['balance']

    if not src_balance >= rep_amount:  # check for needed amount rep on account
        return {'error': "Недостаточно средств", 'error_code': 7}

    src_balance = src_balance - rep_amount
    dst_balance = dst_balance + rep_amount
    engine.execute(accounts_db.update().where(accounts_db.c.id == src_id).values(balance=src_balance))
    engine.execute(accounts_db.update().where(accounts_db.c.id == dst_id).values(balance=dst_balance))
    return {'status': "ok", 'balance': src_balance}
