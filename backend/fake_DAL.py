"""
Fake DAL for testing purposes - uses in-memory data structures
"""
from typing import Any, Dict, List, Optional
from datetime import datetime


# In-memory database simulation
class FakeDB:
    def __init__(self):
        self.users = []
        self.movies = []
        self.messages = []
        self.conversations = []


# Global fake database instances
db_app = FakeDB()
db_vector = FakeDB()


# Users: one document per user
class users_dal:
    @staticmethod
    def insert_one_user(user_data: Dict[str, Any]) -> str:
        user_data["_id"] = f"user_{len(db_app.users)}"
        db_app.users.append(user_data.copy())
        return user_data["_id"]

    @staticmethod
    def find_one_user(filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for user in db_app.users:
            if all(user.get(k) == v for k, v in filter.items()):
                return user.copy()
        return None

    @staticmethod
    def find_all_users() -> List[Dict[str, Any]]:
        return [user.copy() for user in db_app.users]

    @staticmethod
    def update_one_user(filter: Dict[str, Any], update_data: Dict[str, Any]) -> bool:
        for user in db_app.users:
            if all(user.get(k) == v for k, v in filter.items()):
                user.update(update_data)
                return True
        return False

    @staticmethod
    def delete_one_user(filter: Dict[str, Any]) -> bool:
        for i, user in enumerate(db_app.users):
            if all(user.get(k) == v for k, v in filter.items()):
                db_app.users.pop(i)
                return True
        return False


# Movies: one document per movie
class movies_dal:
    @staticmethod
    def insert_one_movie(movie_data: Dict[str, Any]) -> str:
        movie_data["_id"] = f"movie_{len(db_app.movies)}"
        db_app.movies.append(movie_data.copy())
        return movie_data["_id"]

    @staticmethod
    def find_one_movie(filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for movie in db_app.movies:
            if all(movie.get(k) == v for k, v in filter.items()):
                return movie.copy()
        return None

    @staticmethod
    def find_all_movies() -> List[Dict[str, Any]]:
        return [movie.copy() for movie in db_app.movies]

    @staticmethod
    def find_movies_by_user(user_email: str) -> List[Dict[str, Any]]:
        return [
            movie.copy()
            for movie in db_app.movies
            if movie.get("user_email") == user_email
        ]

    @staticmethod
    def update_one_movie(filter: Dict[str, Any], update_data: Dict[str, Any]) -> bool:
        for movie in db_app.movies:
            if all(movie.get(k) == v for k, v in filter.items()):
                movie.update(update_data)
                return True
        return False

    @staticmethod
    def delete_one_movie(filter: Dict[str, Any]) -> bool:
        for i, movie in enumerate(db_app.movies):
            if all(movie.get(k) == v for k, v in filter.items()):
                db_app.movies.pop(i)
                return True
        return False


# Messages: one document per message in a conversation
class messages_dal:
    @staticmethod
    def insert_one_message(message_data: Dict[str, Any]) -> str:
        message_data["_id"] = f"message_{len(db_app.messages)}"
        if "timestamp" not in message_data:
            message_data["timestamp"] = datetime.now()
        db_app.messages.append(message_data.copy())
        return message_data["_id"]

    @staticmethod
    def find_one_message(filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for message in db_app.messages:
            if all(message.get(k) == v for k, v in filter.items()):
                return message.copy()
        return None

    @staticmethod
    def find_all_messages() -> List[Dict[str, Any]]:
        return [message.copy() for message in db_app.messages]

    @staticmethod
    def find_messages_by_convo(convo_id: int) -> List[Dict[str, Any]]:
        messages = [
            message.copy()
            for message in db_app.messages
            if message.get("convo_id") == convo_id
        ]
        # Sort by timestamp
        messages.sort(key=lambda x: x.get("timestamp", datetime.min))
        return messages

    @staticmethod
    def update_one_message(filter: Dict[str, Any], update_data: Dict[str, Any]) -> bool:
        for message in db_app.messages:
            if all(message.get(k) == v for k, v in filter.items()):
                message.update(update_data)
                return True
        return False

    @staticmethod
    def delete_one_message(filter: Dict[str, Any]) -> bool:
        for i, message in enumerate(db_app.messages):
            if all(message.get(k) == v for k, v in filter.items()):
                db_app.messages.pop(i)
                return True
        return False


# Conversations: one document per conversation
class conversations_dal:
    @staticmethod
    def insert_one_conversation(conversation_data: Dict[str, Any]) -> str:
        conversation_data["_id"] = f"convo_{len(db_app.conversations)}"
        if "messages" not in conversation_data:
            conversation_data["messages"] = []
        db_app.conversations.append(conversation_data.copy())
        return conversation_data["_id"]

    @staticmethod
    def find_one_conversation(filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for conversation in db_app.conversations:
            if all(conversation.get(k) == v for k, v in filter.items()):
                return conversation.copy()
        return None

    @staticmethod
    def find_all_conversations() -> List[Dict[str, Any]]:
        return [conversation.copy() for conversation in db_app.conversations]

    @staticmethod
    def find_conversations_by_user(user_email: str) -> List[Dict[str, Any]]:
        return [
            conversation.copy()
            for conversation in db_app.conversations
            if conversation.get("user_email") == user_email
        ]

    @staticmethod
    def update_one_conversation(
        filter: Dict[str, Any], update_data: Dict[str, Any]
    ) -> bool:
        for conversation in db_app.conversations:
            if all(conversation.get(k) == v for k, v in filter.items()):
                conversation.update(update_data)
                return True
        return False

    @staticmethod
    def add_message_to_conversation(
        convo_id: int, message_data: Dict[str, Any]
    ) -> bool:
        for conversation in db_app.conversations:
            if conversation.get("convo_id") == convo_id:
                if "messages" not in conversation:
                    conversation["messages"] = []
                conversation["messages"].append(message_data.copy())
                return True
        return False

    @staticmethod
    def delete_one_conversation(filter: Dict[str, Any]) -> bool:
        for i, conversation in enumerate(db_app.conversations):
            if all(conversation.get(k) == v for k, v in filter.items()):
                db_app.conversations.pop(i)
                return True
        return False
