from fastapi import FastAPI
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean
from sqlalchemy.sql import select
from sqlalchemy import and_
import smtplib
import hashlib
import secrets


def send_mail(destination_mail, mail_subject, mail_text):
    smtp_bot = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_bot.starttls()
    smtp_bot.login('radmirka.tech.mail@gmail.com', '@TechnicalMailPass7210')

    msg_from = "RadmirkaTech"
    msg_to = [destination_mail]
    email_text = f"""\
From: {msg_from}
To: {destination_mail}
Subject: {mail_subject}

{mail_text}"""
    smtp_bot.sendmail(msg_from, msg_to, email_text)
    print("Email sent")
    print(email_text)
    smtp_bot.quit()


def password_sha256_hash(password: str) -> str:
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return password_hash


engine = create_engine('sqlite:///rep_net.db', echo=True)
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

    if (not login.strip()) or (not password.strip()) or (not email.strip()):
        return {'error': "Не все поля заполнены", 'error_code': 1}

    password_hash = password_sha256_hash(password+login)
    verification_code = secrets.token_hex(3)

    registered_logins = engine_connection.execute(select([accounts_db.c.login])).fetchall()
    if (login,) in registered_logins:  # login check
        return {'error': "Логин уже занят", 'error_code': 4}  # error codes for better?
    registered_emails = engine_connection.execute(select([accounts_db.c.email])).fetchall()
    if (email,) in registered_emails:  # email check
        return {'error': "На эту почту уже зарегистрирована учетная запись", 'error_code': 3}  # error codes for better?

    try:  # try to send email with code
        send_mail(email, "Verification code", f"Hello, {login}\nYour verification code is: {verification_code}")
    except smtplib.SMTPRecipientsRefused:  # if email invalid
        return {'error': "invalid email", 'error_code': 8}

    new_acc_insert = accounts_db.insert().values(login=login, email=email,  # new user creation
                                                 password=password_hash, balance=1000,
                                                 verification_code=verification_code,
                                                 email_verification_status=False
                                                 )
    result = engine_connection.execute(new_acc_insert)
    account_id = result.inserted_primary_key

    print(f"new id {account_id}")
    return {'login': login, 'email': email, 'status': "ok", 'id': account_id[0]}


@app.post("/email_verification")
async def email_verification(login: str, user_id: int, verification_code: str):
    if (not login.strip()) or (not str(user_id).strip()) or (not verification_code.strip()):
        return {'error': "Не все поля заполнены", 'error_code': 1}

    print(login, user_id, verification_code)
    db_veref_code = engine_connection.execute(select([accounts_db.c.verification_code])  # local verif code
                                              .where(accounts_db.c.id == user_id)).fetchone()[0]

    token = secrets.token_urlsafe(32)  # token generation

    if verification_code == db_veref_code:  # comparasion with verif code in request
        engine_connection.execute(accounts_db.update()
                                  .where(accounts_db.c.id == user_id)
                                  .values(email_verification_status=True, token=token, verification_code=""))
        return {'status': "ok", 'id': user_id, 'message': "verification successful", 'token': token}
    else:
        return {'id': user_id, 'error': "wrong code", 'error_code': 5}


@app.get("/signin")
@app.post("/signin")
async def signin(login: str, password: str):
    if (not login.strip()) or (not password.strip()):
        return {'error': "Не все поля заполнены", 'error_code': 1}

    password_hash = password_sha256_hash(password+login)

    try:
        engine_connection.execute(select([accounts_db.c.id])
                                  .where(accounts_db.c.login == login)
                                  .where(accounts_db.c.password == password_hash)).fetchone()[0]
    except TypeError:
        return {'error': "Ошибка авторизации", 'error_code': 6}

    # I guess that there can be only one record with such login:password pair
    user_id = engine_connection.execute(select([accounts_db.c.id])
                                        .where(accounts_db.c.login == login)
                                        .where(accounts_db.c.password == password_hash)).fetchone()[0]

    # Check if this account is unverified
    user_email_verification = engine_connection.execute(select([accounts_db.c.email_verification_status])
                                                        .where(accounts_db.c.id == user_id)).fetchone()[0]
    """user_email_verification = engine_connection.execute(select([accounts_db.c.email_verification_status])
                                                        .where(accounts_db.c.login == login)
                                                        .where(accounts_db.c.password == password_hash)).fetchone()[0]"""
    if not user_email_verification:
        return {'error': "Аккаунт не подтвержден", 'login': login, 'user_id': user_id, 'error_code': 2}

    token = secrets.token_urlsafe(32)
    """engine_connection.execute(accounts_db.update()
                              .where(accounts_db.c.login == login).where(accounts_db.c.password == password_hash)
                              .values(token=token))"""
    engine_connection.execute(accounts_db.update().where(accounts_db.c.id==user_id).values(token=token))
    return {'token': token}


def get_id(token):
    # I guess that there can be only one record with such token
    user_id = engine_connection.execute(select([accounts_db.c.id]).where(accounts_db.c.token == token)).fetchone()[0]


def get_all_accounts():
    journal = engine_connection.execute(select([accounts_db.c.login, accounts_db.c.balance])).fetchall()


def get_balance(user_id):
    user_balance = engine_connection.execute(select([accounts_db.c.balance])
                                             .where(accounts_db.c.id == user_id)).fetchone()[0]
    return user_balance


def transfer(src_id: int, dst_id: int, rep_amount: int):
    src_balance = get_balance(src_id)
    dst_balance = get_balance(dst_id)

    if not src_balance >= rep_amount:  # check for needed amount rep on account
        return {'error': "Недостаточно средств", 'error_code': 7}

    src_balance = src_balance - rep_amount
    dst_balance = get_balance(dst_id) + rep_amount
    engine_connection.execute(accounts_db.update().where(accounts_db.c.id == src_id).values(balance=src_balance))
    engine_connection.execute(accounts_db.update().where(accounts_db.c.id == dst_id).values(balance=dst_balance))
    return {'status': "ok", 'balance': src_balance}