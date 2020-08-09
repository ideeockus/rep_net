extends ColorRect


# Declare member variables here. Examples:
# var a = 2
# var b = "text"
var rep_url = "http://127.0.0.1:8000"
var login
var user_id
var token


# Called when the node enters the scene tree for the first time.
func _ready():
	$SignIn.connect("pressed", self, "_on_SignIn_pressed")
	$SignUp.connect("pressed", self, "_on_SignUp_pressed")
	

func _on_SignUp_pressed():
	print("Страница регистрации")
	var SignUpScene = load("res://scenes/SignupScene.tscn")
	print("asd")
	add_child(SignUpScene.instance())
	
	
func _on_SignIn_pressed():
	login = $Login.text
	var password = $Password.text
	
	if (not login) or (not password):
		print("данные не введены")
		return
	#запрос
	var t_url = rep_url+"/signin?login="+login+"&password="+password
	var signin_request = HTTPRequest.new()
	add_child(signin_request)
	signin_request.connect("request_completed", self, "_on_signin_request_completed")
	var headers = ["Content-Type: application/json"]
	signin_request.request(t_url, headers, false, HTTPClient.METHOD_POST)
	#signin_request.queue_free()
	
	
func _on_signin_request_completed(result, response_code, headers, body):
	var json = JSON.parse(body.get_string_from_utf8())
	var response = json.result
	
	if not is_instance_valid(response):
		print("Ошибка на сервере")
		return
	#$HTTPRequest.queue_free()
	
	if 'token' in response:
		token = response['token']
		print(token)
	elif 'error_code' in response:
		error_handler(response)
	else:
		print("Ошибка")
	

func _on_emailverif_request_completed(result, response_code, headers, body):
	var json = JSON.parse(body.get_string_from_utf8())
	var response = json.result
	if not is_instance_valid(response):
		print("Ошибка на сервере")
		return
	
	if 'token' in response:
		token = response['token']
		print(token)
	elif 'error_code' in response:
		error_handler(response)
	else:
		print("Ошибка")
		
	
	
func email_verification(login, user_id):
	var EmailVerifScene = load("res://scenes/EmailVerificationScene.tscn").instance()
	EmailVerifScene.login = login
	EmailVerifScene.user_id = user_id
	add_child(EmailVerifScene)
	
	
	
func error_handler(response):
	var error_code = response['error_code']
	var error_message = response['error']
	#print(int(error_code))
	var e = {
		1: "Rmpty asdasd",
		2: "Ваш аккаунт не подтвержден",
		3: "На этой почте уже зарегестрирован аккаунт",
		4: "К сожалению этот логин уже занят",
		5: "Код верификации неверен",
		6: "Данные для входа не верны",
		7: "На вашем балансе недостаточно средств",
		8: "Проверьте корректность ввода почты",
	}
	#print(e.keys())
	#print(e)
	#print(e[4])
	print(e[int(error_code)])
	if error_code == 2:
		email_verification(response['login'], response['user_id'])


