extends ColorRect


# Declare member variables here. Examples:
# var a = 2
# var b = "text"
#var rep_url = "http://127.0.0.1:8000"
var rep_url = "https://repnet.herokuapp.com"
var login
var user_id
var token


# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.
	

func _on_SignUp_pressed():
	login = $Login.text.http_escape()
	var email = $Email.text.http_escape()
	var password = $Password.text.http_escape()
	
	if (not login) or (not password):
		print("поля пусты")
		return
	
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
	print(response)
	if 'user_id' in response:
		user_id = response['user_id']
		token = email_verification(login, user_id)
	elif 'error_code' in response:
			error_handler(response)
			print("error code in response")
	else:
		print("error")
		print("probably wrong api")
	
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
		2: "Ваш аккаунт не подтвержден",
		3: "На этой почте уже зарегестрирован аккаунт",
		4: "К сожалению этот логин уже занят",
		5: "Код верификации неверен",
		6: "Данные для входа не верны",
		7: "На вашем балансе недостаточно средств",
		8: "Проверьте корректность ввода почты",
		9: "Неверный токен",
	}
	print(e[int(error_code)])
	if error_code == 2:
		email_verification(response['login'], response['user_id'])


