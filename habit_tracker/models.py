from django.db import models

from users.models import User

# Create your models here.
class ConversationState(models.Model):
    # Define states for the conversation
    INITIAL = 'INITIAL'
    ASK_NAME = 'ASK_NAME'
    ASK_PERSONAL_INTENT = 'ASK_PERSONAL_INTENT'
    ASK_JOURNAL_START = 'ASK_JOURNAL_START'
    ASK_SUMMARY = 'ASK_SUMMARY'
    ASK_WIN = 'ASK_WIN'
    ASK_IMPROVEMENT = 'ASK_IMPROVEMENT'
    ASK_INTENT_PROMPT = 'ASK_INTENT_PROMPT'
    FINISHED = 'FINISHED'

    # Choices for state field
    STATE_CHOICES = (
        (INITIAL, 'Initial'),
        (ASK_NAME, 'Ask Name'),
        (ASK_PERSONAL_INTENT, 'Ask Personal Intent'),
        (ASK_JOURNAL_START, 'Ask Journal Start'),
        (ASK_SUMMARY, 'Ask Summary'),
        (ASK_WIN, 'Ask Win'),
        (ASK_IMPROVEMENT, 'Ask Improvement'),
        (ASK_INTENT_PROMPT, 'Ask Intent Prompt'),
        (FINISHED, 'Finished'),
    )

    # Fields for the state model
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default=INITIAL)

class JournalEntry(models.Model):
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # responses
    response1 = models.TextField()
    response2 = models.TextField()
    response3 = models.TextField()
    response4 = models.TextField()

    # respnse summaries
    summary1 = models.TextField(default='')
    summary2 = models.TextField(default='')
    summary3 = models.TextField(default='')
    master_summary = models.TextField(default='')

    is_complete = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)