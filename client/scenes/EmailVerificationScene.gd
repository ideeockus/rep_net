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
	$OK_button.connect("pressed", self, "_on_ok_button_pressed")
	
func _on_ok_button_pressed():
	var verification_code = $Code.text
	if (not login) or (not verification_code) or (not user_id):
		return
	
	#print(login, user_id, verification_code)
	#запрос
	var t_url = rep_url+"/email_verification?login="+login+"&user_id="+str(user_id)+"&verification_code="+str(verification_code)
	var emailverif_request = HTTPRequest.new()
	add_child(emailverif_request)
	emailverif_request.connect("request_completed", self, "_on_emailverif_request_completed")
	var headers = ["Content-Type: application/json"]
	emailverif_request.request(t_url, headers, false, HTTPClient.METHOD_POST)
	

func _on_emailverif_request_completed(result, response_code, headers, body):
	var json = JSON.parse(body.get_string_from_utf8())
	var response = json.result
	print(response)
	
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
		9: "Неверный токен",
	}
	print(e[int(error_code)])
	if error_code == 2:
		print("OOPS STRANGE ERROR")


# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass
