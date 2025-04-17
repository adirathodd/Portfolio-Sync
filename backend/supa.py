import os
from supabase import create_client, Client
from dotenv import load_dotenv
from utils import files_req, files_opt, users_opt, users_req
import bcrypt
from datetime import datetime

load_dotenv()

class UserManager:
    def __init__(self):
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, )

    def hash(self, item: str):
        return bcrypt.hashpw(
            item.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
    
    def verify(self, username: str, password: str):
        """Verify a user's credentials."""
        try:
            response = (
                self.supabase
                    .table("users")
                    .select("password")
                    .eq("username", username)
                    .execute()
            )

            if not response.data:
                return (False, "Incorrect username or password!")
            
            stored_hash = response.data[0]["password"]
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                return (True, "Login successful!")
            
            return (False, "Incorrect username or password!")
        except Exception as e:
            return (False, f"Error logging in user: {e}")

    def update_user(self, user_id: int, updates: dict):
        """Updates the given fields for a particular user."""
        try:
            allowed_fields = users_req + users_opt
            for key in updates:
                if key not in allowed_fields:
                    raise KeyError(f"Unexpected key in updates: {key}")

            if "password" in updates:
                updates["password"] = self.hash(updates["password"])

            response = (
                self.supabase
                    .table("users")
                    .update(updates)
                    .eq("id", user_id)
                    .execute()
            )

            if not response.data:
                raise KeyError(f"No user found with id: {user_id}")
        
            return (True, "User updated succesfully!")
        except Exception as e:
            return (False, f"Error updating user: {e}")

    def add_user(self, user_data: dict):
        """Add a new user to the 'users' table."""
        try:
            new_user = {}

            for column in users_req:
                if column not in user_data:
                    raise KeyError(f"Required field missing: {column}")
                
                new_user[column] = user_data[column]
                user_data.__delitem__(column)
            
            for column in user_data:
                if column not in users_opt:
                    raise KeyError(f"Unexpected field: {column}")
                
                new_user[column] = user_data[column]

            new_user["password"] = self.hash(new_user["password"])

            self.supabase.table("users").insert(new_user).execute()
            return (True, "Sign up completed!")
        except Exception as e:
            return(False, f"Error creating the user: {e}")

    def remove_user(self, user_id: int):
        """Remove a user from the 'users' table by user id."""
        try:
            response = (
                self.supabase
                    .table("users")
                    .delete()
                    .eq("id", user_id)
                    .execute()
            )


            if not response.data:
                raise KeyError(f"No user found with id: {user_id}")
            
            return (True, "User deleted!")
        except Exception as e:
            return (False, f"Error deleting the user: {e}")

if __name__ == '__main__':
    um = UserManager()
    
    # Example: List all users
    # response = um.list_users()
    # print("Current users:", response)
    
    # Example: Add a new user (uncomment to use)
    # new_user = {"username": "john_doe", "email": "john@example.com", "password": "hello", "first_name": "John",
    #             "last_name": "Doe"}
    # print("Added user:", um.add_user(new_user))
    
    # Example: Remove a user by id (uncomment to use)
    print("Removed user:", um.remove_user(5))