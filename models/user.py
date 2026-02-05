class User:
    def __init__(self, id, username, email, plan="free"):
        self.id = id
        self.username = username
        self.email = email
        self.plan = plan