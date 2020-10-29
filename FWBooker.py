import schedule
from requests import Session
import datetime
from schedule import *
import time

site = "https://www.fitnessworld.com/dk2/?destination=/dk2/front%3Fgclid" \
       "%3DEAIaIQobChMIkqr5ypHQ7AIVi9eyCh1SuAOAEAMYASAAEgKKovD_BwE "

login_data = {
    "form_build_id": "form-Kp7lr53EWjgme-FOXI9w-Kqi1yqxQMzj5HQnTGk6Xes",
    "form_id": "user_login_form",
    "name": "X",
    "pass": "Y",
    "redirect_url": "",
    "op": "Log+ind"
}

dayoffset = 21

# for the query, fw allows 21 days reach at 00:00
opendate = (datetime.datetime.now() + datetime.timedelta(days=21))
year = opendate.year
month = opendate.month
day = opendate.day
classes = {
    'Bike Base': '23741',
    'Bike Standard': '23742',
    'Bike Edge': '23743'
}

centers = {
    'Forum': '164'
}
forum = centers.get('Forum')

with Session() as s:
    login = s.post(site, login_data)
    content_of_resp = login.content
    assert b"\"userLoginStatus\":\"loggedIn\"", "Error Not Logged In, Check Username+Password"

    request_url = "https://www.fitnessworld.com/dk2/api/search_activities?classes%5B%5D=23743&" \
                  f"classes%5B%5D=23742&classes%5B%5D=23741&centers%5B%5D={forum}&" \
                  f"from={year}-{month}-{day}&to={year}-{month}-{day + 1}"
    response = s.get(request_url)
    booking_resp = response.json()[0]

# if __name__ == "__main__":
#     print("hello world")
# def job():
#     print("Im working")
#
#
# schedule.every().minute.at(":17").do(job)
# while True:
#     schedule.run_pending()
#     time.sleep(1)
#
