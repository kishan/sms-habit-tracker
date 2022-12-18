from django.shortcuts import render

from users.models import User

# basic cleaning of cell phone number
def clean_cellphone(cellphone):
    # if longer than 10 characters, get last 10 digits
    # Ex. +19992224444 => 9992224444
    if len(str(cellphone)) > 10:
        return str(cellphone)[-10:]
    
# fetch user by cellphone number
# return None if user cannot be found
def get_user_by_cellphone(cellphone):
    cellphone = clean_cellphone(cellphone)
    try:
        user = User.objects.get(cellphone=str(cellphone))
        return user
    except User.DoesNotExist:
        return None
    