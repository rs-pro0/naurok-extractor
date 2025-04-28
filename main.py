import requests
from http.cookies import SimpleCookie
from datetime import datetime, timedelta
from lxml import html
import json

set_cookies = []
with open("cookies.json", "r") as f:
    set_cookies = json.load(f)
proxies = {
    "http": "http://127.0.0.1:8082",
    "https": "http://127.0.0.1:8082",
}

cookie = SimpleCookie()

session = requests.Session()

for set_cookie in set_cookies:
    cookie = SimpleCookie()
    cookie.load(set_cookie)
    for key, morsel in cookie.items():
        session.cookies.set(key, morsel.value)

test_url="https://naurok.com.ua/test/prava-nepovnolitnih-u-trudovomu-pravi-2852786/set"
set_page = session.get(test_url)
tree = html.fromstring(set_page.text)
csrf_token = tree.xpath('//meta[@name="csrf-token"]/@content')[0]
afterset_page = session.post(test_url,data={
    "_csrf": csrf_token,
    "Homework[name]":"Тест",
    "Homework[deadline_day]":(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
    "Homework[deadline_hour]":"23:59",
    "Homework[shuffle_question]":"0",
    "Homework[shuffle_options]":"0",
    "Homework[shuffle_options]":"1",
    "Homework[show_answer]":"0",
    "Homework[show_review]":"0",
    "Homework[show_review]":"1",
    "Homework[show_leaderbord]":"0",
    "Homework[show_leaderbord]":"1",
    "Homework[available_attempts]":"0",
    "Homework[duration]":"40",
    "Homework[show_timer]":"0",
    "Homework[show_flashcard]":"0",
    "Homework[show_match]":"0",
})
response_url = afterset_page.url
homework_id = response_url.split("/")[-1]
tree = html.fromstring(afterset_page.text)
homework_code = tree.xpath('//span[@class="homework-code"]/text()')[0]
game_url = f"https://naurok.com.ua/test/join?gamecode={homework_code}"
game_start_page = session.get(game_url)
tree = html.fromstring(game_start_page.text)
csrf_token = tree.xpath('//meta[@name="csrf-token"]/@content')[0]
game_page = session.post(game_url, data={
    "_csrf": csrf_token,
    "JoinForm[gamecode]": homework_code,
    "JoinForm[name]": "test",
})
test_uuid = game_page.url.split("/")[-1]
tree = html.fromstring(game_page.text)
session_id = tree.xpath('//div[@ng-app="testik"]/@ng-init')[0].split(",")[1]
test_session_url = f"https://naurok.com.ua/api2/test/sessions/{session_id}"
test_main_page = session.get(test_session_url)
test_json = test_main_page.json()
first_question_id = test_json["questions"][0]["id"]
first_question_answer_id = test_json["questions"][0]["options"][0]["id"]
test_answer_url = f"https://naurok.com.ua/api2/test/responses/answer"
session.put(test_answer_url, json={
    "session_id": session_id,
    "answer": [
        first_question_answer_id
    ],
    "question_id": first_question_id,
    "show_answer": 1,
    "type": "quiz",
    "point": "1",
    "homeworkType": 1,
    "homework": True
})
test_session_end_url = f"https://naurok.com.ua/api2/test/sessions/end/{session_id}"
session.put(test_session_end_url)
test_completion_url = f"https://naurok.com.ua/test/complete/{test_uuid}"
test_completion_page = session.get(test_completion_url)
tree = html.fromstring(test_completion_page.text)

questions = tree.xpath('//div[contains(@class, "homework-stat-question-line")][p]')
for i in questions:
    print(i.xpath("./p[1]")[0].text_content())
    for j in i.xpath('.//div[contains(@class, "homework-stat-option-value") and contains(@class, "correct")]/p[1]'):
        print("+", j.text_content())
    for j in i.xpath('.//div[contains(@class, "homework-stat-option-value") and contains(@class, "incorect")]/p[1]'):
        print("-", j.text_content())
homework_url = f"https://naurok.com.ua/test/homework/{homework_id}"
homework_page = session.get(homework_url)
tree = html.fromstring(homework_page.text)
csrf_token = tree.xpath('//meta[@name="csrf-token"]/@content')[0]
homework_delete_url = f"https://naurok.com.ua/test/homework/{homework_id}/delete"
homework_delete_page = session.post(homework_delete_url, data={
    "_csrf":csrf_token,
})
