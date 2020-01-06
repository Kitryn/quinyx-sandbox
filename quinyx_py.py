import requests
import datetime
from enum import IntEnum


class ShiftStatus(IntEnum):
    MY_SHIFTS = 1
    UNASSIGNED = 2
    SWAPPABLE = 4
    COLLEAGUE = 8
    NOTICE_OF_INTEREST = 16
    SHIFT_BOOKINGS = 32
    ABSENCE = 64


def _shift_type(*args):
    output = 0
    for status in args:
        output += status
    return str(output)


class ApiError(Exception):
    pass


class Quinyx:
    _BASE_URL = "https://app.quinyx.com/api/"
    _OAUTH_URL = "2.0/oauth/token"
    _LOGIN_URL = "1.2/user/login?appVersion=2.36.1&OS=iOS"
    _SCHEDULE_URL = "1.2/user/schedule"
    _FILTER_URL = "1.2/user/schedule/filter"
    _LEAVE_URL = "1.2/user/leave"

    # Matching what the app sends out
    _BASE_HEADERS = {"Connection": "keep-alive", "Accept": "application/json",
                     "User-Agent": "Quinyx/2.36.1.2 (iPhone; iOS 11.4; Scale/2.00)", "Accept-Language": "en",
                     "Accept-Encoding": "gzip, deflate"}

    # not needed; Requests doesn't add charset though I think?
    # _ADDON_JSON_HEADERS = {"Content-Type": "application/json; charset=utf-8"}

    def __init__(self, debug_cert=None):
        self.s = requests.Session()
        self.s.headers.update(self._BASE_HEADERS)

        if debug_cert:  # if using mitmproxy to inspect traffic
            self.s.verify = debug_cert

    def _url(self, path):
        return self._BASE_URL + path

    def request(self, method, url, **kwargs):
        r = self.s.request(method, url, **kwargs)
        if not r.ok:
            raise ApiError("{} {} {}".format(method, url, r.status_code))
        return r

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)

    def login(self, username, password):
        payload = {"grantType": "password",
                   "username": username,
                   "password": password}
        r = self.post(self._url(self._OAUTH_URL), json=payload)
        self.s.headers.update({"Authorization": "Bearer " + r.json()["token"]["accessToken"]})
        return r  # what should this return?

    def get_schedule(self):
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=today.weekday())

        schedule = []
        payload = {"days": "180",
                   "fromDate": start_date.isoformat(),
                   "page": "0",
                   "perPage": "50",
                   "shiftType": _shift_type(ShiftStatus.MY_SHIFTS, ShiftStatus.SWAPPABLE, ShiftStatus.UNASSIGNED,
                                            ShiftStatus.NOTICE_OF_INTEREST, ShiftStatus.COLLEAGUE,
                                            ShiftStatus.SHIFT_BOOKINGS),
                   "categoryIds": "261176,252028,261174,261418,261175,261419,270346",
                   "sectionIds": "53680"}  # get all shifts at this location
        r = self.get(self._url(self._SCHEDULE_URL), params=payload)
        json_response = r.json()
        schedule += json_response["schedule"]
        if int(json_response["pagination"]["totalPages"]) > 1:
            for i in range(1, int(json_response["pagination"]["totalPages"])):
                payload["page"] = str(i)
                r = self.get(self._url(self._SCHEDULE_URL), params=payload)
                schedule += r.json()["schedule"]

        return schedule

    def get_schedule_filter(self):
        r = self.get(self._url(self._FILTER_URL))
        return r.json()

    def get_leave_schedule(self, from_date, to_date):
        # GET https://app.quinyx.com/api/1.2/user/leave?fromDate=2019-05-01&toDate=2021-04-30&type=leaveschedule
        raise NotImplementedError()

    def get_leave_applications(self):
        # GET https://app.quinyx.com/api/1.2/user/leave?type=leaveapps
        raise NotImplementedError()

    def get_notice_of_interest(self):
        # GET https://app.quinyx.com/api/1.2/user/noi
        raise NotImplementedError()

    def get_news(self):
        # GET https://app.quinyx.com/api/1.2/user/news
        raise NotImplementedError()

