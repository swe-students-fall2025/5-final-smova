import os

from typing import Any, Dict, List, Optional

# see if we are in testing mode
TESTING = os.environ.get("TESTING") == "1"

if TESTING:
    # use the fake DAL for testing
    from backend.fake_DAL import (
        db,
        users_dal,
        movies_dal,
        messages_dal,
        conversations_dal,
    )
else:
    from dotenv import load_dotenv
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError
    from pymongo.server_api import ServerApi

    # Load environment variables from .env
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

    MONGODB_CONNECTION = os.getenv("MONGO_URI")
    DB_NAME = os.getenv("MONGO_DB")

    if not MONGODB_CONNECTION or not DB_NAME:
        raise RuntimeError(
            "MONGO_URI and MONGO_DB must be set in the .env file"
        )

    client = MongoClient(MONGODB_CONNECTION)
    client.admin.command("ping")
    db = client.get_database(DB_NAME)

    # Users: one document per user
    class users_dal:
        @staticmethod
        def insert_one_user(user_data: Dict[str, Any]) -> str:
            try:
                result = db.users.insert_one(user_data)
                return str(result.inserted_id)
            except PyMongoError as e:
                print(f"Error inserting user: {e}")
                return ""

        @staticmethod
        def find_one_user(filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            try:
                return db.users.find_one(filter)
            except PyMongoError as e:
                print(f"Error finding user: {e}")
                return None

        @staticmethod
        def find_all_users() -> List[Dict[str, Any]]:
            try:
                return list(db.users.find({}))
            except PyMongoError as e:
                print(f"Error finding users: {e}")
                return []

        @staticmethod
        def update_one_user(
            filter: Dict[str, Any], update_data: Dict[str, Any]
        ) -> bool:
            try:
                result = db.users.update_one(filter, {"$set": update_data})
                return result.modified_count > 0
            except PyMongoError as e:
                print(f"Error updating user: {e}")
                return False

        @staticmethod
        def delete_one_user(filter: Dict[str, Any]) -> bool:
            try:
                result = db.users.delete_one(filter)
                return result.deleted_count > 0
            except PyMongoError as e:
                print(f"Error deleting user: {e}")
                return False

    # Movies: one document per movie
    class movies_dal:
        @staticmethod
        def insert_one_movie(movie_data: Dict[str, Any]) -> str:
            try:
                result = db.movies.insert_one(movie_data)
                return str(result.inserted_id)
            except PyMongoError as e:
                print(f"Error inserting movie: {e}")
                return ""

        @staticmethod
        def find_one_movie(filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            try:
                return db.movies.find_one(filter)
            except PyMongoError as e:
                print(f"Error finding movie: {e}")
                return None

        @staticmethod
        def find_all_movies() -> List[Dict[str, Any]]:
            try:
                return list(db.movies.find({}))
            except PyMongoError as e:
                print(f"Error finding movies: {e}")
                return []

        @staticmethod
        def find_movies_by_user(user_email: str) -> List[Dict[str, Any]]:
            """Find all movies associated with a user (if user_email is stored in movie)"""
            try:
                return list(db.movies.find({"user_email": user_email}))
            except PyMongoError as e:
                print(f"Error finding movies by user: {e}")
                return []

        @staticmethod
        def update_one_movie(
            filter: Dict[str, Any], update_data: Dict[str, Any]
        ) -> bool:
            try:
                result = db.movies.update_one(filter, {"$set": update_data})
                return result.modified_count > 0
            except PyMongoError as e:
                print(f"Error updating movie: {e}")
                return False

        @staticmethod
        def delete_one_movie(filter: Dict[str, Any]) -> bool:
            try:
                result = db.movies.delete_one(filter)
                return result.deleted_count > 0
            except PyMongoError as e:
                print(f"Error deleting movie: {e}")
                return False

    # Messages: one document per message in a conversation
    class messages_dal:
        @staticmethod
        def insert_one_message(message_data: Dict[str, Any]) -> str:
            try:
                result = db.messages.insert_one(message_data)
                return str(result.inserted_id)
            except PyMongoError as e:
                print(f"Error inserting message: {e}")
                return ""

        @staticmethod
        def find_one_message(filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            try:
                return db.messages.find_one(filter)
            except PyMongoError as e:
                print(f"Error finding message: {e}")
                return None

        @staticmethod
        def find_all_messages() -> List[Dict[str, Any]]:
            try:
                return list(db.messages.find({}))
            except PyMongoError as e:
                print(f"Error finding messages: {e}")
                return []

        @staticmethod
        def find_messages_by_convo(convo_id: int) -> List[Dict[str, Any]]:
            """Find all messages for a specific conversation"""
            try:
                return list(db.messages.find({"convo_id": convo_id}).sort("timestamp", 1))
            except PyMongoError as e:
                print(f"Error finding messages by conversation: {e}")
                return []

        @staticmethod
        def update_one_message(
            filter: Dict[str, Any], update_data: Dict[str, Any]
        ) -> bool:
            try:
                result = db.messages.update_one(filter, {"$set": update_data})
                return result.modified_count > 0
            except PyMongoError as e:
                print(f"Error updating message: {e}")
                return False

        @staticmethod
        def delete_one_message(filter: Dict[str, Any]) -> bool:
            try:
                result = db.messages.delete_one(filter)
                return result.deleted_count > 0
            except PyMongoError as e:
                print(f"Error deleting message: {e}")
                return False

    # Conversations: one document per conversation
    class conversations_dal:
        @staticmethod
        def insert_one_conversation(conversation_data: Dict[str, Any]) -> str:
            try:
                result = db.conversations.insert_one(conversation_data)
                return str(result.inserted_id)
            except PyMongoError as e:
                print(f"Error inserting conversation: {e}")
                return ""

        @staticmethod
        def find_one_conversation(filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            try:
                return db.conversations.find_one(filter)
            except PyMongoError as e:
                print(f"Error finding conversation: {e}")
                return None

        @staticmethod
        def find_all_conversations() -> List[Dict[str, Any]]:
            try:
                return list(db.conversations.find({}))
            except PyMongoError as e:
                print(f"Error finding conversations: {e}")
                return []

        @staticmethod
        def find_conversations_by_user(user_email: str) -> List[Dict[str, Any]]:
            """Find all conversations for a specific user"""
            try:
                return list(db.conversations.find({"user_email": user_email}))
            except PyMongoError as e:
                print(f"Error finding conversations by user: {e}")
                return []

        @staticmethod
        def update_one_conversation(
            filter: Dict[str, Any], update_data: Dict[str, Any]
        ) -> bool:
            try:
                result = db.conversations.update_one(filter, {"$set": update_data})
                return result.modified_count > 0
            except PyMongoError as e:
                print(f"Error updating conversation: {e}")
                return False

        @staticmethod
        def add_message_to_conversation(
            convo_id: int, message_data: Dict[str, Any]
        ) -> bool:
            """Add a message to a conversation's messages array"""
            try:
                result = db.conversations.update_one(
                    {"convo_id": convo_id}, {"$push": {"messages": message_data}}
                )
                return result.modified_count > 0
            except PyMongoError as e:
                print(f"Error adding message to conversation: {e}")
                return False

        @staticmethod
        def delete_one_conversation(filter: Dict[str, Any]) -> bool:
            try:
                result = db.conversations.delete_one(filter)
                return result.deleted_count > 0
            except PyMongoError as e:
                print(f"Error deleting conversation: {e}")
                return False

