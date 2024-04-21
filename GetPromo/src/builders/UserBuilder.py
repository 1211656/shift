


def user_insert(username,email,password):
    print("Chegou aqui")
    from app import User, db
    new_user = User(email=email,password=password,username=username)
    db.session.add(new_user)
    try:

        db.session.commit()
        return True
    except Exception as e:

        db.session.rollback()
        return False
