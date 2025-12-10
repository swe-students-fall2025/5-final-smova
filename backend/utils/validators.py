import re

def validate_registration_data(data):
    errors = {}

    fname = data.get("fname")
    if not fname or not isinstance(fname, str) or not fname.strip():
        errors["fname"] = "First name is required."

    lname = data.get("lname")
    if not lname or not isinstance(lname, str) or not lname.strip():
        errors["lname"] = "Last name is required."

    email = data.get("email")
    if not email or not isinstance(email, str):
        errors["email"] = "Email is required."
    else:
        email_regex = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
        if not re.match(email_regex, email):
            errors["email"] = "Invalid email format."

    password = data.get("password")
    if not password or not isinstance(password, str):
        errors["password"] = "Password is required."
    elif len(password) < 6:
        errors["password"] = "Password must be at least 6 characters long."

    return len(errors)==0, ""


def validate_login_data(data):
    errors = {}
    email = data.get("email")
    if not email or not isinstance(email, str):
        errors["email"] = "Email is required."
    else:
        email_regex = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
        if not re.match(email_regex, email):
            errors["email"] = "Invalid email format."
    password = data.get("password")
    if not password or not isinstance(password, str):
        errors["password"] = "Password is required."
    return len(errors)==0,""


def validate_chat_message(data):
    errors = {}

    content = data.get("content")
    if not content or not isinstance(content, str) or not content.strip():
        errors["content"] = "Message content is required."



    convo_id = data.get("convo_id")
    if convo_id is None:
        errors["convo_id"] = "Conversation ID (convo_id) is required."
    else:
        try:
            int(convo_id)
        except (ValueError, TypeError):
            errors["convo_id"] = "convo_id must be a numeric value."
    return len(errors)==0, ""


def validate_movie_data(data):
    errors = {}

    movie_name = data.get("movie_name")
    if not movie_name or not isinstance(movie_name, str) or not movie_name.strip():
        errors["movie_name"] = "Movie name is required."

    movie_id = data.get("movie_id")
    if movie_id is None:
        errors["movie_id"] = "movie_id is required."
    else:
        try:
            int(movie_id)
        except (ValueError, TypeError):
            errors["movie_id"] = "movie_id must be a numeric value."

    movie_description = data.get("movie_description")
    if movie_description is not None and not isinstance(movie_description, str):
        errors["movie_description"] = "movie_description must be a string."

    has_watched = data.get("has_watched")
    if has_watched is not None and not isinstance(has_watched, bool):
        errors["has_watched"] = "has_watched must be true or false."

    rating = data.get("rating")
    if rating is not None:
        try:
            float(rating)
        except (ValueError, TypeError):
            errors["rating"] = "rating must be a numeric value."

    return len(errors)==0, ""

    
