"""
create a user repository that will be used to interact with the database
"""




class UserRepository:
    @staticmethod
    async def get_by_username(username: str):
        """
        retrieve a user by their username
        """
        pass


    @staticmethod
    async def create(username: str):
        """
        create a new user
        """
        pass

    @staticmethod
    async def get_most_recent(n: int):
        """
        get n most recent users
        """
        pass