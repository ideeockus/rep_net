extends ColorRect


# Declare member variables here. Examples:
# var a = 2
# var b = "text"
var rep_url = "http://127.0.0.1:8000"
var token
var user_id
var button_dst_id


# Called when the node enters the scene tree for the first time.
func _ready():
	#запрос журнала пользователей
	var j_url = rep_url+"/journal"
	var journal_request = HTTPRequest.new()
	add_child(journal_request)
	journal_request.connect("request_completed", self, "_on_journal_request_completed")
	var headers = ["Content-Type: application/json"]
	journal_request.request(j_url, headers, false, HTTPClient.METHOD_POST)
	
	#запрос баланса
	var b_url = rep_url+"/get_balance?user_id="+str(user_id)
	var balance_request = HTTPRequest.new()
	add_child(balance_request)
	balance_request.connect("request_completed", self, "_on_balance_request_completed")
	#var headers = ["Content-Type: application/json"]
	balance_request.request(b_url, headers, false, HTTPClient.METHOD_POST)


# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass
func _on_journal_request_completed(result, response_code, headers, body):
	var json = JSON.parse(body.get_string_from_utf8())
	var response = json.result
	print(response)
	for user in response['journal']:
		var person_button_text = str(user['id'])+" "+user['login']+" "+str(user['balance'])
		
		var person_button = Button.new()
		person_button.text = person_button_text
		#person_button.theme.set_font()
		person_button.set("custom_fonts/font", load("res://rep_font.tres"))
		#person_button.set("custom_colors/font_color", "#000000")
		person_button.align = Button.ALIGN_LEFT
		# person_button.person_id = user['id']
		person_button.connect("pressed", self, "_on_person_button_pressed")
		$ScrollContainer/PersonsContainer.add_child(person_button)
		
		
func _on_balance_request_completed(result, response_code, headers, body):
	var json = JSON.parse(body.get_string_from_utf8())
	var response = json.result
	print(response)
	var user_balance = response['balance']
	$HBoxContainer/Balance.text = str(user_balance)
	
	
func _on_person_button_pressed():
	pass

