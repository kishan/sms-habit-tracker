from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse

from habit_tracker.lib_gpt3 import gpt3_get_ai_chat_response

from users.views import get_user_by_cellphone

from .lib_twilio import send_sms

from users.models import User

def index(request):
    return HttpResponse("Hello, world.")

# Endpoint for responding to incoming SMS messages to our Twilio number
@require_POST
@csrf_exempt # TODO: address CSRF if deploying to production
def sms_reply(request):
    msg_body = ''
    media_link = ''

    user_cellphone = request.POST.get('From', '')
    incoming_msg = request.POST.get('Body', '').lower()
    print(f'-----\nreceived following message from {user_cellphone}: {incoming_msg}')

    # get user by phone #
    user = get_user_by_cellphone(user_cellphone)
    if not user:
        # TODO: trigger onboarding flow
        print('no user with this phone number was found')
        build_twilio_reply_response('sorry, we did not find user account associated with this number')
    else:
        print('user was found: ' + user.get_first_name())

    # determine response to incoming message
    if incoming_msg=='yo':
        msg_body = 'yo dawg!'
    elif incoming_msg=='1':
        msg_body = 'Gotta love a GIF!'
        media_link= 'https://i.imgur.com/BwmtaWS.gif'
    elif incoming_msg=='2':
        msg_body='Enjoy this image!'
        media_link='https://i.imgur.com/zNxhPjp.jpeg'
    elif incoming_msg=='3':
        msg_body='Have a wonderful day'
    elif incoming_msg=='menu':
        msg_body='Here are some options to consider. \n\nReply with:\n1 to receive a GIF \n2 for an image \n3 for an SMS!'
    else:
        # use GPT3 as default reply
        msg_body = gpt3_get_ai_chat_response(incoming_msg)

    # prepend name introduction to text
    if user:
        intro_str = f"hey {user.get_first_name()}!\n\n"
        msg_body = intro_str + msg_body

    print(f'-----\nresponding to text with:\n{msg_body}\n-----\n')

    twilio_reply_response = build_twilio_reply_response(msg_body, media_link)
    return twilio_reply_response

def build_twilio_reply_response(msg_body='', media_link = ''):
    # create Twilio response
    response = MessagingResponse()

    msg = response.message(str(msg_body))
    if media_link:
        msg.media(media_link)

    return HttpResponse(response)
    

# Endpoint for sending SMS message from Twilio number
def sms_test(request):
    # send text to user1 (kishan)
    user = User.objects.get(id=1)
    send_sms(user.cellphone, f"hey {user.get_first_name()} This is a test.")

    # send_sms_to_all_users()
    return HttpResponse('text sent')

def send_sms_to_all_users():
    users = User.objects.all()
    for user in users:
        print("sending test text to: " + user.get_first_name() + " at " + user.cellphone)
        if user.cellphone:
            send_sms(user.cellphone, f"hey {user.get_first_name()}! This is a test.")

def sms_test_morning_reminder(request):
    user = User.objects.get(id=1)
    send_morning_reminder(user)
    return HttpResponse('morning reminder sent')

def send_morning_reminder(user: User):
    # TODO: pull habits for given user
    habit_name = 'Test Habit'
    sms_text = f"Good morning {user.get_first_name()} 🌤️ Don't forget to complete your habit for today: {habit_name}"
    send_sms(user.cellphone, sms_text)