import datetime
from django.utils import timezone
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse

from habit_tracker.lib_gpt3 import gpt3_create_day_summary_message, gpt3_create_exciting_response_about_user_intention, gpt3_create_master_summary, gpt3_create_personal_intention_prompt, gpt3_get_ai_chat_response, gpt3_summarize_response1, gpt3_summarize_response2, gpt3_summarize_response3, gpt3_create_personal_intention_feedback
from habit_tracker.models import ConversationState, JournalEntry

from users.views import create_user_with_cellphone, get_user_by_cellphone, split_full_name

from .lib_twilio import send_sms

from users.models import User

def index(request):
    return HttpResponse("Hello, world.")

# Endpoint for responding to incoming SMS messages to our Twilio number
@require_POST
@csrf_exempt # TODO: address CSRF if deploying to production
def receive_sms(request):
    msg_body = ''
    media_link = ''

    user_cellphone = request.POST.get('From', '')
    incoming_msg = request.POST.get('Body', '').lower().strip()
    print(f'-----\nreceived message from {user_cellphone}\n-----\n')

    # get user by phone #
    user = get_user_by_cellphone(user_cellphone)
    if not user:
        # if no user with this phone number found, then cerate new user and kickoff onboarding flow
        print('no user with this phone number was found')
        user = create_user_with_cellphone(user_cellphone)
        state = ConversationState(user=user, state=ConversationState.ASK_NAME)
        state.save()
        print(f'successfully created new user. ID = {str(user.id)} phone = {user.cellphone}. State = {ConversationState.ASK_NAME}')
        return build_twilio_reply_response('👋 Hi!\n\nWelcome to GoWrtite: your personalized AI journal assistant. 📕 \n\nPlease reply with your full name to get started')

    # fetch state of covnersation to check if we are in middle of conversation
    state = ConversationState.objects.filter(user=user).first()
    print(f'incoming_msg: {incoming_msg[:30]}')
    print(f'current state: {state.state}')
    if incoming_msg=='delete':
        # backdoor command to delete user for testing purposes
        print(f'deleting user {user.get_first_name()} with id = {user.id}')
        user.delete()
        return build_twilio_reply_response('successfully deleted your user account')
    elif incoming_msg=='summarize':
        send_day_recap_messages(user)
        return HttpResponse()
    elif incoming_msg=='yo':
        msg_body = 'yo dawg!'
    elif incoming_msg=='week':
        msg_body = get_weekly_recap_hardcoded_sample()
    elif incoming_msg=='start':
        # hard-coded command to manually kick off journaling flow
        entry_exists = JournalEntry.objects.filter(date=datetime.date.today(), user=user).exists()
        if entry_exists:
            x = 1
            # TODO: return early if user already journaled for today
            # return build_twilio_reply_response("You've already filled out your journal for today! Please check back in tomorrow.")
        kickoff_reflection_reminder(user)
        return HttpResponse()
    elif state.state == ConversationState.ASK_NAME:
        # Get user's name from their response and save to DB
        full_name =  request.POST.get('Body', '').title()
        (first_name, last_name) = split_full_name(full_name)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # update state to finished since no further action needed from user
        state.state = ConversationState.ASK_PERSONAL_INTENT
        state.save()
        print('updated state to ASK_PERSONAL_INTENT')

        msg_body = f'''hey {user.get_first_name()}! Excited to have you on board. 🚀\n\nI'll be your partner to form a consistent journaling practice and deliver personalized experience so we can focus on what's most valuable for you.\n\nTo start please share me one intention or goal you'd love to focus on for the next few weeks. Answer with "I want to focus on"'''
    elif state.state == ConversationState.ASK_PERSONAL_INTENT:
        # Get user's name from their response and save to DB
        personal_intention =  request.POST.get('Body', '')
        user.personal_intention = personal_intention
        user.save()

        # update state to finished since no further action needed from user
        state.state = ConversationState.FINISHED
        state.save()
        print('updated state to FINISHED')

        excitment_response = gpt3_create_exciting_response_about_user_intention(user)

        msg_body = f'''{excitment_response}\n\nMoving forward I\'ll text you every evening at 8pm PT to guide you through your daily reflection. If you can't wait, reply 'start' to jump into your journal reflection right now.'''
    elif state.state == ConversationState.ASK_JOURNAL_START:
        # confirm if user wants to start
        journal_start_response =  request.POST.get('Body', '').lower()
        print(f'journal_start_response: {journal_start_response}')
        if journal_start_response == 'yes':
            # update to next state
            state.state = ConversationState.ASK_SUMMARY
            state.save()
            print('updated state to ASK_SUMMARY')

            # create new journal entry
            journal_entry = JournalEntry(date=datetime.date.today(), user=user)
            journal_entry.save()

            msg_body = f'''Great! Let's get started. I'll walk you through a series of prompts. Just reply back directly within one message and I'll record your responses.\n\nPrompt #1:\nHow would you summarize your day today? What did you do & any reflections? (the more details the better)'''
        else:
            state.state = ConversationState.FINISHED
            state.save()
            print('updated state to FINISHED')

            msg_body = f'''Seems like now is not a great time to reflect. Respond anytime with 'start' when you are ready.'''
    elif state.state == ConversationState.ASK_SUMMARY:
        # Retrieve current journal entry and save user response
        summary_response =  request.POST.get('Body', '')
        entry = JournalEntry.objects.filter(date=datetime.date.today(), user=user, is_complete=False).first()
        entry.response1 = summary_response
        entry.save()

        # update to next state
        state.state = ConversationState.ASK_WIN
        state.save()
        print('updated state to ASK_WIN')

        msg_body = f'''Prompt #2:\nWhat was your biggest win of the day?'''
    elif state.state == ConversationState.ASK_WIN:
         # Retrieve current journal entry and save user response
        win_response =  request.POST.get('Body', '')
        entry = JournalEntry.objects.filter(date=datetime.date.today(), user=user, is_complete=False).first()
        entry.response2 = win_response
        entry.save()

        # update to next state
        state.state = ConversationState.ASK_IMPROVEMENT
        state.save()
        print('updated state to ASK_IMPROVEMENT')

        msg_body = f'''Prompt #3:\nWhat could you have done better today?'''
    elif state.state == ConversationState.ASK_IMPROVEMENT:
         # Retrieve current journal entry and save user response
        improvement_response =  request.POST.get('Body', '')
        entry = JournalEntry.objects.filter(date=datetime.date.today(), user=user, is_complete=False).first()
        entry.response3 = improvement_response
        entry.save()

        # update to next state
        state.state = ConversationState.ASK_INTENT_PROMPT
        state.save()
        print('updated state to ASK_INTENT_PROMPT')

        # form personalized prompt related to user's custom intent
        # user_custom_intention = 'I want to focus more on community and belonging in my life.'
        custom_intention_prompt = gpt3_create_personal_intention_prompt(user)

        msg_body = f'''Prompt #4:\n{custom_intention_prompt}'''
    elif state.state == ConversationState.ASK_INTENT_PROMPT:
        # Retrieve current journal entry and save user response
        personal_intent_response =  request.POST.get('Body', '')
        entry = JournalEntry.objects.filter(date=datetime.date.today(), user=user, is_complete=False).first()
        entry.response4 = personal_intent_response
        entry.is_complete = True
        entry.completed_at = timezone.make_aware(datetime.datetime.now())
        entry.save()

        # update to next state
        state.state = ConversationState.FINISHED
        state.save()
        print('updated state to FINISHED')

        send_day_recap_messages(user)
        return HttpResponse()
    else:
        # use GPT3 as default reply
        msg_body = gpt3_get_ai_chat_response(incoming_msg)

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

def kickoff_reflection_reminder(user: User):
    # TODO: make sure user has not already journaled for today
    state = ConversationState.objects.filter(user=user).first()
    if not state:
        print(f'NO state founder for user w/ id = {user.id}')
        return
    # update to next state
    state.state = ConversationState.ASK_JOURNAL_START
    state.save()
    print('updated state to ASK_JOURNAL_START\n')
    
    sms_text = f"Hey {user.get_first_name()}!\n\nAre you available for ~5min to do your daily reflection right now? Respond with yes/no."
    send_sms(user.cellphone, sms_text)

def generate_response_summaries(user, entry):
    response1 = entry.response1
    response2 = entry.response2
    response3 = entry.response3

    summary1 = gpt3_summarize_response1(user, response1)
    summary2 = gpt3_summarize_response2(user, response2)
    summary3 = gpt3_summarize_response3(user, response3)

    # create master summary from all summaries of first 3 prompts
    master_summary = gpt3_create_master_summary(user, summary1, summary2, summary3)

    entry.summary1 = summary1
    entry.summary2 = summary2
    entry.summary3 = summary3
    entry.master_summary = master_summary
    entry.save()

def send_day_recap_messages(user):
    # backdoor command to ....

    ### Message 1
    send_sms(user.cellphone, f'Great reflecting {user.first_name}!👏 Consistency is key and kudos for following through today.\n\nHere are a few thoughts summarizing your day.')
    completed_entry = JournalEntry.objects.filter(date=datetime.date.today(), user=user, is_complete=True).first()
    print(f'summarizing entry id = {completed_entry.id}')

    ### Message 2
    generate_response_summaries(user, completed_entry)
    day_summary_message = gpt3_create_day_summary_message(user,  completed_entry.master_summary)
    send_sms(user.cellphone, f'{day_summary_message}')

    ### Message 3
    user_custom_intention = user.get_personal_intention()
    response4 = completed_entry.response4
    custom_intention_feedback = gpt3_create_personal_intention_feedback(user, response4)
    send_sms(user.cellphone, f'💌 Progress on your intention: "{user_custom_intention}"\n----------\n{custom_intention_feedback}')

     ### Message 4
    send_sms(user.cellphone, f'''Great job completing your reflection today 🙌 See you tomorrow!''')

    return None

def get_weekly_recap_hardcoded_sample():
    return '''
Play-by-Play Highlight Summary of the Week:
⭐ Monday: You scored the winning shot in a basketball game with your friends!
⭐ Tuesday: You made the tough but necessary task of booking tickets to visit your family.
⭐ Wednesday: You made a huge breakthrough on your hackathon project and had a great dinner with friends.
⭐ Thursday: You took some time to relax and appreciate the beauty of nature, and attended a community event.
⭐ Friday: You pushed through and finished the last few pieces of your project.
⭐ Saturday: You had a memorable day out with your friends at the beach.

Themes:
| Theme                      | Count |
|----------------------------|-------|
| Friends                         | 3     |
| Community                    | 1     |
| Projects/Hobby              | 3     |
| Relaxation/Nature          | 1     |
| Accomplishment/Pride    | 3    |
| Necessary Tasks             | 1     |
'''