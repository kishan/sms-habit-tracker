from django.db import models

from users.models import User

# Create your models here.
class ConversationState(models.Model):
    # Define states for the conversation
    INITIAL = 'INITIAL'
    ASK_NAME = 'ASK_NAME'
    ASK_JOURNAL_START = 'ASK_JOURNAL_START'
    ASK_SUMMARY = 'ASK_SUMMARY'
    ASK_WIN = 'ASK_WIN'
    ASK_IMPROVEMENT = 'ASK_IMPROVEMENT'
    FINISHED = 'FINISHED'

    # Choices for state field
    STATE_CHOICES = (
        (INITIAL, 'Initial'),
        (ASK_NAME, 'Ask Name'),
        (ASK_JOURNAL_START, 'Ask Journal Start'),
        (ASK_SUMMARY, 'Ask Summary'),
        (ASK_WIN, 'Ask Win'),
        (ASK_IMPROVEMENT, 'Ask Improvement'),
        (FINISHED, 'Finished'),
    )

    # Fields for the state model
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default=INITIAL)