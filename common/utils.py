from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.pagination import PageNumberPagination
from app_account.models import Notification, User
import os, re


class CustomRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context['response'].status_code
        response = {
            "status": "success",
            "code": status_code,
            "data": data,
            "message": None
        }
        if not str(status_code).startswith('2'):
            response["status"] = "error"
            response["data"] = None

            if 'detail' in data:
                response["message"] = data["detail"]
            else:
                response['message'] = dict2string(data)

        return super(CustomRenderer, self).render(response, accepted_media_type, renderer_context)


# pagination default class
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


# convert serializer error into json error
def dict2string(data):
    msg = ""
    print(data)
    for key in data.keys():
        print(key)
        print(data[key][0])
        if key == "non_field_errors":
            msg += str(data[key][0]) + "\n\r"
        else:
            # if type(data[key]) == list:
            #     print("mmmmm")
            #     print(data[key][0])
            # print(data[key])
            # print(type(data[key]))
            msg += key + ": " + str(data[key][0]) + "\n\r"
    return msg


def notify_managers(user, title, message):
    managers = User.objects.filter(clinic=user.clinic, is_active=True, role="M")
    for manager in managers:
        notification = Notification(
            user=manager,
            sender=user,
            title=title,
            brief=message
        )
        notification.save()

    solo = User.objects.filter(clinic=user.clinic, is_active=True, role="S")
    for manager in solo:
        notification = Notification(
            user=manager,
            sender=user,
            title=title,
            brief=message
        )
        notification.save()


 
def is_valid_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    return email and isinstance(email, str) and re.fullmatch(regex, email)


def deNoise(text):
    noise = re.compile(""" ّ    | # Tashdid
                             َ    | # Fatha
                             ً    | # Tanwin Fath
                             ُ    | # Damma
                             ٌ    | # Tanwin Damm
                             ِ    | # Kasra
                             ٍ    | # Tanwin Kasr
                             ْ    | # Sukun
                             ـ     # Tatwil/Kashida
                         """, re.VERBOSE)
    text = re.sub(noise, '', text)
    return text


def removeNonArabic(text):
    text = re.sub("[A-Za-z0-9]", "@", text)
    return text


def dictReplace(text, dic):
    for k, v in dic.items():
        text = text.replace(k, v)
    return(text)


def dictReplaceRev(text, dic):
    for k, v in dic.items():
        text = text.replace(v, k)
    return(text)


translit = {
    '،'   : ',',
# letters
    'ء'  : 'a',
    'ؤ'  : 'w',
    'ئ'  : 'i',
    'ا'  : 'a',
    'إ'  : 'e',
    'أ'  : 'a',
    'آ'  : 'a',
    'ب'  : 'b',
    'ة'  : 't',
    'ت'  : 't',
    'ث'  : 'th',
    'ج'  : 'j',
    'ح'  : 'h',
    'خ'  : 'gh',
    'د'  : 'd',
    'ذ'  : 'th',
    'ر'  : 'r',
    'ز'  : 'z',
    'س'  : 's',
    'ش'  : 'sh',
    'ص'  : 's',
    'ض'  : 'd',
    'ط'  : 't',
    'ظ'  : 'd',
    'ع'  : 'a',
    'غ'  : 'gh',
    'ف'  : 'f',
    'ق'  : 'q',
    'ك'  : 'k',
    'ل'  : 'l',
    'م'  : 'm',
    'ن'  : 'n',
    'ه'  : 'h',
    'و'  : 'w',
    'ى'  : 'a',
    'ي'  : 'y',
}

