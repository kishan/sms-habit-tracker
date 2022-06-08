from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse

from .lib_twilio import send_sms, make_call

def index(request):
    return HttpResponse("Hello, world.")

# Endpoint for responding to incoming SMS messages to our Twilio number
@require_POST
@csrf_exempt # TODO: address CSRF if deploying to production
def sms_reply(request):
    incoming_msg = request.POST.get('Body', '').lower()

    # create Twilio response
    response = MessagingResponse()

    msg_body = ''
    media_link = ''

    if incoming_msg=='yo':
        msg_body = 'yo dawg'
    elif incoming_msg=='1':
        msg_body = 'Gotta love a GIF!'
        media_link= 'https://i.imgur.com/BwmtaWS.gif'
    elif incoming_msg=='2':
        msg_body='Enjoy this image!'
        media_link='https://i.imgur.com/zNxhPjp.jpeg'
    elif incoming_msg=='3':
        msg_body='Have a wonderful day'
    else:
        msg_body="""\nInvalid Option. \n\nWelcome to Habbit Buddy! 🎉 \n\nReply with:\n1 to receive a GIF \n2 for an image \n3 for an SMS!"""

    msg = response.message(str(msg_body))
    if media_link:
        msg.media(media_link)

    return HttpResponse(response)

# Endpoint for sending SMS message from Twilio number
def sms_test(request):
    send_sms(settings.USER_TEST_NUMBER, "hi! This is a test.")
    return HttpResponse('text sent')

def sms_test_morning_reminder(request):
    send_morning_reminder()
    return HttpResponse('morning reminder sent')

def send_morning_reminder():
    # TODO: pull all habits that are due for today, and fetch associated users

    # for now hardcode with test user
    user_number = settings.USER_TEST_NUMBER
    user_name = 'Test User'
    habit_name = 'Test Habit'
    sms_text = f"Good morning {user_name}! Don't forget to complete your habit for today: {habit_name}"
    send_sms(user_number, sms_text)