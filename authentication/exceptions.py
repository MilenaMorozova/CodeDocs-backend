class AuthenticationException(Exception):
    def __init__(self, message, response_status):
        self.message = message
        self.response_status = response_status


class FieldNotGivenException(AuthenticationException):
    def __init__(self, field_name):
        super().__init__(f"{field_name} not given", 400)


class IllegalFieldException(AuthenticationException):
    def __init__(self, field_name):
        super().__init__(f"{field_name} is incorrect", 406)


class FieldIsNotUniqueException(AuthenticationException):
    def __init__(self, field_name):
        super().__init__(f"This {field_name} is already in use", 409)


class UserDoesNotExistException(AuthenticationException):
    def __init__(self):
        super().__init__("User does not exist", 404)


# class UserAlreadyExistException(AuthenticationException):
#     def __init__(self):
#         super().__init__("This user already exist", 400)
