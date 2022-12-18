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
    
# Create new user in the database
def create_user_with_cellphone(cellphone):
    cellphone = clean_cellphone(cellphone)
    user = User.objects.create(cellphone=cellphone)
    return user

def add_names_to_user(user, first_name, last_name):
    user.first_name = first_name
    user.last_name = last_name
    user.save()

# split full name into first and last name
def split_full_name(full_name):
 
  words = full_name.split()
  
  # If the list has at least two elements, return the first element as the first name and the rest of the string as the last name
  if len(words) >= 2:
    first_name = words[0]
    last_name = " ".join(words[1:])
    return first_name, last_name
  
  # If the list has only one element, return it as the first name and an empty string as the last name
  elif len(words) == 1:
    first_name = words[0]
    last_name = ""
    return first_name, last_name
  
  # If the list is empty, return empty strings for both first and last name
  else:
    return "", ""