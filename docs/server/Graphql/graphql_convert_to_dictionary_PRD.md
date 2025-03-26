Convert to Dictionary

Strawberry provides a utility function to convert a Strawberry object to a dictionary.

You can use strawberry.asdict(...) function:

@strawberry.type
class User:
    name: str
    age: int


# should be {"name": "Lorem", "age": 25}
user_dict = strawberry.asdict(User(name="Lorem", age=25))
  