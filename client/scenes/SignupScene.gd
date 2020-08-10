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
	pass # Replace with function body.
	

func _on_SignUp_pressed():
	login = $Login.text
	var email = $Email.text
	var password = $Password.text
	
	if (not login) or (not password):
		print("поля пусты")
		return
	
	#var signup_req = JSON.print({'login': login, 'email': email, 'password': password})
	#print(JSON.parse(signup_req).result)
	# запрос для регистрации
	var t_url = rep_url+"/signup?login="+login+"&email="+email+"&password="+password
	var signup_request = HTTPRequest.new()
	add_child(signup_request)
	signup_request.connect("request_completed", self, "_on_signup_request_completed")
	var headers = ["Content-Type: application/json"]
	signup_request.request(t_url, headers, false, HTTPClient.METHOD_POST)


func _on_SignIn_pressed():
	print("на страницу входа..")
	queue_free()
	

func _on_signup_request_completed(result, response_code, headers, body):
	var json = JSON.parse(body.get_string_from_utf8())
	
	var response = json.result
	"""if not is_instance_valid(response):
		print("Ошибка на сервере")
		return"""
	print(response)
	if 'id' in response:
		user_id = response['id']
		token = email_verification(login, user_id)
	elif 'error_code' in response:
			error_handler(response)
			print("error code in response")
	else:
		print("error")
		_on_SignUp_pressed()
	

func _on_emailverif_request_completed(result, response_code, headers, body):
	var json = JSON.parse(body.get_string_from_utf8())
	var response = json.result
	if not is_instance_valid(response):
		print("Ошибка на сервере")
		return
	
	if 'token' in response:
		token = response['token']
		print(token)
		var JournalScene = load("res://scenes/JournalScene.tscn").instance()
		JournalScene.user_id = response['user_id']
		JournalScene.token = response['token']
		add_child(JournalScene)
	elif 'error_code' in response:
		error_handler(response)
	else:
		print("Ошибка")
		
	
	
func email_verification(login, user_id):
	var EmailVerifScene = load("res://scenes/EmailVerificationScene.tscn").instance()
	EmailVerifScene.login = login
	EmailVerifScene.user_id = user_id
	add_child(EmailVerifScene)
	
	"""if (not login) or (not verification_code):
		return
	
	#запрос
	var t_url = rep_url+"/email_verification?login="+login+"&user_id="+user_id+"&verification_code="+verification_code
	var emailverif_request = HTTPRequest.new()
	add_child(emailverif_request)
	emailverif_request.connect("request_completed", self, "_on_emailverif_request_completed")
	var headers = ["Content-Type: application/json"]
	emailverif_request.request(t_url, headers, false, HTTPClient.METHOD_POST)"""
	
	
func error_handler(response):
	var error_code = response['error_code']
	var error_message = response['error']
	#print(int(error_code))
	var e = {2: "Ваш аккаунт не подтвержден",
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


