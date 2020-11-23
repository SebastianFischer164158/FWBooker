import schedule
import time
from requests import Session
from schedule import *

DAY_OFFSET = 21

# should probably be held in a csv file or similar.
classes_dict = {
    'Bike Base': '23741',
    'Bike Standard': '23742',
    'Bike Edge': '23743'
}

centers_dict = {
    'Forum': '164'
}


def login_to_fw(username, password):
    site_url = "https://www.fitnessworld.com/dk2/?destination=/dk2/front" \
               "%3Fgclid%3DEAIaIQobChMIkqr5ypHQ7AIVi9eyCh1SuAOAEAMYASAAE" \
               "gKKovD_BwE "

    login_data = {
        "form_build_id": "form-Kp7lr53EWjgme-FOXI9w-Kqi1yqxQMzj5HQnTGk6Xes",
        "form_id": "user_login_form",
        "name": username,
        "pass": password,
        "redirect_url": "",
        "op": "Log+ind"
    }

    with Session() as sess:
        login = sess.post(site_url, login_data)
        content_of_resp = login.content
        if b"\"userLoginStatus\":\"loggedIn\"" not in content_of_resp:
            raise Exception("Error Not Logged In, Check Username+Password")
        else:
            return sess


def retrieve_class(session_, center, year, month, dayx, dayy, classes):
    class_string = ''
    class_prefix = 'classes%5B%5D='
    for a_class in classes:
        classID = classes_dict.get(a_class)
        class_string += class_prefix + classID + '&'

    request_url = "https://www.fitnessworld.com/dk2/api/search_activities?" \
                  f"{class_string}centers%5B%5D={center}&" \
                  f"from={year}-{month}-{dayx}&to={year}-{month}-{dayy}"
    response = session_.get(request_url)
    possible_bookings = response.json()[0]
    return possible_bookings


def book_an_activity(session_, bookingID, activityID):
    booking_url = 'https://www.fitnessworld.com/dk2/api/book_activity'
    booking_data = {
        'bookingId': bookingID,
        'activityId': activityID,
        'payment_type': 'free'
    }
    booking_resp = session_.post(booking_url, booking_data).json()
    print(" ----> ", booking_resp)

    if booking_resp['status'] == 'success':
        print(f"Booked activityID {activityID} bookingID {bookingID}")
        return booking_resp['participationId']
    else:
        raise Exception(f"Could not book activityID {activityID} with"
                        f"bookingID {bookingID}")


def unbook_activity(session_, particiID):
    unbooking_url = 'https://www.fitnessworld.com/dk2/api/unbook_activity'
    unbooking_data = {'participationId': particiID}
    unbooking_resp = session_.post(unbooking_url, unbooking_data).json()
    if unbooking_resp['status'] == 'success':
        print(f"Unbooked with ParticipationID {particiID}")
        return 0
    else:
        raise Exception(f"Could not unbook  {particiID}")


def login_and_book(username: str, password: str, centerID: str, classes):
    print(f"{login_and_book.__name__} executed at {datetime.datetime.now()}")
    orig_session = login_to_fw(username=username, password=password)

    # for the query, fw allows 21 days reach at 00:00
    opendate = (datetime.datetime.now() + datetime.timedelta(days=DAY_OFFSET))
    future_yr = opendate.year
    future_mnth = opendate.month
    future_day = opendate.day

    psb_bookings = retrieve_class(session_=orig_session, center=centerID,
                                  year=future_yr, month=future_mnth,
                                  dayx=future_day, dayy=future_day,
                                  classes=classes)
    print(psb_bookings)

    possible_classes = psb_bookings['items']
    ac_bk_IDs = [(x['activityId'], x['bookingId']) for x in possible_classes]
    print(ac_bk_IDs)

    participationIDs = []
    for activityID, bookingID in ac_bk_IDs:
        resp = book_an_activity(session_=orig_session, bookingID=bookingID,
                                activityID=activityID)
        participationIDs.append(resp)

    print(participationIDs)
    return 0

    # for participationID in participationIDs:
    #     unbook_activity(session_=orig_session, particiID=participationID)


if __name__ == "__main__":
    Forum = centers_dict.get('Forum')
    classes = ['Bike Base', 'Bike Standard', 'Bike Edge']
    random_element = random.randint(1, 59)
    random_element = '0' + str(random_element) if random_element <= 9 \
        else str(random_element)
    starttime = f'00:00:{random_element}'
    # login_and_book(username = "",password = "", centerID = Forum,classes = classes)
    schedule.every().day.at(starttime).do(login_and_book, username="",
                                          password="", centerID=Forum,
                                          classes=classes)
    while True:
        schedule.run_pending()
        time.sleep(1)
    # do check with ps auxf | grep python and check if it is scheduled
    # if it is not there then cat nohup txt file and check the "log"
