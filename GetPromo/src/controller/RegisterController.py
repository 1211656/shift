


def register_verification(username,email,password1,password2):
    from app import User
    if username==None:
        return False
    if email==None:
        return False
    if password1==None:
        return False
    if password2==None:
        return False

    user_with_username = User.query.filter_by(username=username).first()
    print("Chegou aqui")
    if user_with_username:
        return False
    user_with_email = User.query.filter_by(email=email).first()
    if user_with_email:
        return False

    if password1!=password2:
        return False

    return True