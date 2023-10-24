from app import USERS, POSTS
import re


class User:
    def __init__(self, id, first_name, last_name, email):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.total_reactions = 0
        self.posts = []

    def add_post(self, post):
        self.posts.append(post.id)
        POSTS.append(post)

    def to_json(self):
        """Function that reformat data to dictionary for json"""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "total_reactions": self.total_reactions,
        }

    def __lt__(self, other):
        return self.total_reactions < other.total_reactions


class Post:
    def __init__(self, id, author_id, text):
        self.id = id
        self.author_id = author_id
        self.text = text
        self.reactions = []
        USERS[author_id].add_post(self)

    def add_reaction(self, reaction):
        self.reactions.append(reaction)
        USERS[self.author_id].total_reactions += 1
        self.__sort_post()

    def __sort_post(self):
        """Private function that sorts user posts in descending order of reactions"""
        if len(USERS[self.author_id].posts) >= 2:
            for i in range(len(USERS[self.author_id].posts) - 1, 0, -1):
                if (
                    POSTS[USERS[self.author_id].posts[i]]
                    > POSTS[USERS[self.author_id].posts[i - 1]]
                ):
                    (
                        USERS[self.author_id].posts[i],
                        USERS[self.author_id].posts[i - 1],
                    ) = (
                        USERS[self.author_id].posts[i - 1],
                        USERS[self.author_id].posts[i],
                    )

    def to_json(self):
        """Function that reformat data to dictionary for json"""
        return {
            "id": self.id,
            "author_id": self.author_id,
            "text": self.text,
            "reactions": self.reactions,
        }

    def __lt__(self, other):
        return len(self.reactions) < len(other.reactions)


class Validator:
    """The class that helps validate data"""

    @staticmethod
    def is_valid_email(email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    @staticmethod
    def is_email_unique(email):
        return email in {user.email for user in USERS}

    @staticmethod
    def is_valid_user(user_id):
        return 0 <= user_id < len(USERS)

    @staticmethod
    def is_valid_post(post_id):
        return 0 <= post_id < len(POSTS)

    @staticmethod
    def is_valid_reaction(reaction):
        reactions = ["like", "dislike", "heart", "boom", "capybara"]
        return reaction in reactions

    @staticmethod
    def is_valid_sort(type_sort):
        return type_sort in {"asc", "desc"}

    @staticmethod
    def is_valid_leaderboard(type_ld):
        return type_ld in {"list", "graph"}
