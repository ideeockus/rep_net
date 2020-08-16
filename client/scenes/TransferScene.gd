extends ColorRect


# Declare member variables here. Examples:
# var a = 2
# var b = "text"
#var rep_url = "http://127.0.0.1:8000"
var rep_url = "https://repnet.herokuapp.com"
var src_id
var dst_id
var token
var user_login
var person_login


# Called when the node enters the scene tree for the first time.
func _ready():
	$VBoxContainer/UserName.text = user_login
	$InfoLabel.text = "перевод "+str(person_login)
	
	#запрос баланса
	var b_url = rep_url+"/get_balance?user_id="+str(src_id)
	var balance_request = HTTPRequest.new()
	add_child(balance_request)
	balance_request.connect("request_completed", self, "_on_balance_request_completed")
	var headers = ["Content-Type: application/json"]
	balance_request.request(b_url, headers, false, HTTPClient.METHOD_POST)
	
	$HBoxContainer2/SendButton.connect("pressed", self, "_on_send_button_pressed")
	$BackButton.connect("pressed", self, "_on_back_button_pressed")
	

func _on_balance_request_completed(result, response_code, headers, body):
	var json = JSON.parse(body.get_string_from_utf8())
	var response = json.result
	print(response)
	# в случае ошибки
	if 'error_code' in response:
		error_handler(response)
		return
		
	var user_balance = response['balance']
	$VBoxContainer/HBoxContainer/Balance.text = str(user_balance)
	
	
func _on_send_button_pressed():
	var amount = $HBoxContainer2/Amount.text
	if not amount.is_valid_integer():
		return
	
	var t_url = rep_url+"/transfer?src_id="+str(src_id)+"&dst_id="+str(dst_id)+\
	"&rep_amount="+str(amount)+"&token="+str(token)
	var transfer_request = HTTPRequest.new()
	add_child(transfer_request)
	transfer_request.connect("request_completed", self, "_on_transfer_request_completed")
	var headers = ["Content-Type: application/json"]
	transfer_request.request(t_url, headers, false, HTTPClient.METHOD_POST)
	

func _on_transfer_request_completed(result, response_code, headers, body):
	var json = JSON.parse(body.get_string_from_utf8())
	var response = json.result
	print(response)
	# в случае ошибки
	if 'error_code' in response:
		error_handler(response)
		return
		
	var user_balance = response['balance']
	$VBoxContainer/HBoxContainer/Balance.text = str(user_balance)
	
	get_parent().update()
	queue_free()
	
	
func _on_back_button_pressed():
	queue_free()
	

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
	#print(e.keys())
	#print(e)
	#print(e[4])
	print(e[int(error_code)])


# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass
