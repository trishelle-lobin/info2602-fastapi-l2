import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User
from fastapi import Depends
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

cli = typer.Typer()

@cli.command()
def initialize():
    with get_session() as db: # Get a connection to the database
        drop_all() # delete all tables
        create_db_and_tables() #recreate all tables
        bob = User(username='bob', email='bob@mail.com', password='bobpass') # Create a new user (in memory)
        db.add(bob) # Tell the database about this new data
        db.commit() # Tell the database persist the data
        db.refresh(bob) # Update the user (we use this to get the ID from the db)
        print("Database Initialized")

@cli.command()
def get_user(username:str= typer.Argument(...,help="The username of the user to be printed")):
    """
    Retrieves a user by their username and prints the username.
    If a username is not found an error message is outputted.
    """
    with get_session() as db: # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found!')
            return
        print(user)

@cli.command()
def get_all_users():
    # The code for task 5.2 goes here. Once implemented, remove the line below that says "pass"
      with get_session() as db:
        all_users = db.exec(select(User)).all()
        if not all_users:
            print("No users found")
        else:
            for user in all_users:
                print(user)


@cli.command()
def change_email(username: str= typer.Argument(...,help="The username of the user to be printed"), 
                 new_email:str=typer.Argument(...,help="The email of the user to be changed/altered")):
    """
    Retrieves a user by their username and updates thedir email.
    If a username is not found an error message is outputted.
    """
    with get_session() as db: # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to update email.')
            return
        user.email = new_email
        db.add(user)
        db.commit()
        print(f"Updated {user.username}'s email to {user.email}")

@cli.command()
def create_user(username: str=typer.Argument(...,help="The username of the user to be created"), 
                email:str=typer.Argument(...,help="The email of the user to be created"), 
                password: str=typer.Argument(...,help="The password of the user to be created")):
     """
     Retrieves a user by their username,email and password and creates a new user.
     If a username is already taken an error message is outputted.
     """
     with get_session() as db: # Get a connection to the database

        newuser = User(username=username, email=email, password=password)
        try:
            db.add(newuser)
            db.commit()
        except IntegrityError as e:
            db.rollback() #let the database undo any previous steps of a transaction
            #print(e.orig) #optionally print the error raised by the database
            print("Username or email already taken!") #give the user a useful message
        else:
            print(newuser) # print the newly created user

@cli.command()
def delete_user(username: str=typer.Argument(...,help="The username of the user to be deleted")):
     """
    Retrieves a user by their username and deletes the user.
    If a username is not found an error message is outputted.
    """
     with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to delete user.')
            return
        db.delete(user)
        db.commit()
        print(f'{username} deleted')
#render

@cli.command()
def emailorusername(username:str=typer.Argument(...,help="The username of the user to be printed")):
    with get_session() as db: # Get a connection to the database
        #user = db.exec(select(User).where(User.username == user)).first() 
        """
        Retrieves a user by their username or email and prints the user.
        If a username or email is not found an error message is outputted.
        """
        all_users = db.exec(select(User)).all()
        found=False
        for users in all_users:
            if (username in users.username or username in users.email):
                print(users)
                found=True
        if (found==False):
            print('The user was not found!')


@cli.command()
def get_users(limit:int=typer.Argument(10, help="List the first N users of the database to be used by a paginated table"),
              offset:int=typer.Argument(0, help="Set to 0")):
      """
    List the first N users of the database to be used by a paginated table.
    The loop ends when the counter has reached the limit
    """
    # The code for task 5.1 goes here. Once implemented, remove the line below that says "pass"
      with get_session() as db: # Get a connection to the database
        all_users = db.exec(select(User)).all()
        count=-1
        for users in all_users:
            count+=1
            if count>=offset and count<limit+offset:
                print(users)            
            if count==limit+offset:
                break
            
if __name__ == "__main__":
    cli()