extends ColorRect


# Declare member variables here. Examples:
# var a = 2
# var b = "text"
#var rep_url = "http://127.0.0.1:8000"
var rep_url = "https://repnet.herokuapp.com"
var token
var user_id
var user_login = ""
#var button_dst_id


# Called when the node enters the scene tree for the first time.
func _ready():
	update()

func update():
	# обнуление списка
	for journal_person in $ScrollContainer/PersonsContainer.get_children():
		journal_person.queue_free()
	
	#запрос журнала пользователей
	var j_url = rep_url+"/journal"
	var journal_request = HTTPRequest.new()
	add_child(journal_request)
	journal_request.connect("request_completed", self, "_on_journal_request_completed")
	var headers = ["Content-Type: application/json"]
	journal_request.request(j_url, headers, false, HTTPClient.METHOD_POST)
	
	#запрос баланса   ### ctrl+k because balance check moved to get_journal function
#	var b_url = rep_url+"/get_balance?user_id="+str(user_id)
#	var balance_request = HTTPRequest.new()
#	add_child(balance_request)
#	balance_request.connect("request_completed", self, "_on_balance_request_completed")
#	#var headers = ["Content-Type: application/json"]
#	balance_request.request(b_url, headers, false, HTTPClient.METHOD_POST)


# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass
func _on_journal_request_completed(result, response_code, headers, body):
	var json = JSON.parse(body.get_string_from_utf8())
	var response = json.result
	print(response)
	# в случае ошибки
	if 'error_code' in response:
		error_handler(response)
		return
		
	for user in response['journal']:
		if user['id'] == user_id:  # user['id'] here because it is directly from DB
			user_login = user['login']
			$VBoxContainer/UserName.text = user_login
			$VBoxContainer/HBoxContainer/Balance.text = str(user['balance'])
			continue
		var person_button_text = "    "+user['login']+" "+str(user['balance'])
		
		var person_button = Button.new()
		person_button.text = person_button_text
		#person_button.theme.set_font()
		person_button.set("custom_fonts/font", load("res://rep_font.tres"))
		#person_button.set("custom_colors/font_color", "#000000")
		person_button.align = Button.ALIGN_LEFT
		# person_button.person_id = user['id']
		person_button.connect("pressed", self, "_on_person_button_pressed", [user['id'], user['login']])
		$ScrollContainer/PersonsContainer.add_child(person_button)
		
		
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
	
	
func _on_person_button_pressed(person_id, person_login):
	print(person_id)
	var TransferScene = load("res://scenes/TransferScene.tscn").instance()
	TransferScene.src_id = user_id  # от кого
	TransferScene.dst_id = person_id  # кому
	TransferScene.user_login = user_login
	TransferScene.person_login = person_login  # логин
	TransferScene.token = token  # token
	add_child(TransferScene)


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
