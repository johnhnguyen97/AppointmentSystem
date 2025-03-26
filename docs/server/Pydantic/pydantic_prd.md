# Pydantic Configuration Guide

## Overview
This document outlines our standards and best practices for using Pydantic v2 in the application.

## Key Changes in Pydantic v2

### Configuration
1. Use `model_config` instead of `class Config`:
```python
from pydantic import BaseModel, ConfigDict

class MyModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        validate_default=True
    )
    # fields here
```

2. For settings, use `SettingsConfigDict`:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=True
    )
    # settings here
```

### Common Errors

1. **Config and model_config Both Defined**
```python
# INCORRECT ❌
class Model(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    class Config:  # This will raise PydanticUserError
        from_attributes = True

# CORRECT ✅
class Model(BaseModel):
    model_config = ConfigDict(from_attributes=True)
```

2. **Using Old Config Methods**
```python
# INCORRECT ❌
class Settings(BaseSettings):
    class Config:
        env_file = ".env"

# CORRECT ✅
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
```

## Best Practices

1. **Settings Configuration**
- Use `SettingsConfigDict` for all settings classes
- Provide explicit types for all settings
- Use environment variables for sensitive data
- Set appropriate default values

2. **Model Configuration**
- Use `ConfigDict` for Pydantic models
- Enable `from_attributes=True` when working with ORMs
- Set `validate_default=True` for stricter validation
- Use `frozen=True` for immutable models

3. **Type Hints**
- Always use type hints for all fields
- Use `Optional[]` for nullable fields
- Use `Union[]` for fields that can have multiple types
- Use `Annotated[]` for fields with metadata

4. **Validation**
- Use field validators for complex validation
- Use computed fields for derived values
- Implement custom validators when needed
- Use `Field()` for field metadata and constraints

## Security Considerations

1. **Sensitive Data**
- Don't include sensitive data in model dumps
- Use `exclude` in model configuration for sensitive fields
- Use environment variables for secrets
- Implement field-level encryption when needed

2. **Input Validation**
- Always validate input data
- Set appropriate field constraints
- Use custom validators for complex rules
- Validate data at the model level

## Performance Optimization

1. **Model Configuration**
- Use `frozen=True` for immutable models
- Enable `validate_assignment=False` when not needed
- Use `arbitrary_types_allowed=True` only when necessary
- Consider `copy_on_model_validation=False` for large models

2. **Caching**
- Cache validated models when appropriate
- Use model copy instead of revalidation when possible
- Consider using Redis for model caching
- Implement cache invalidation strategies

## Example Implementations

### Base Model Example
```python
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class UserModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        strict=True
    )

    username: str = Field(..., min_length=3)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    age: Optional[int] = Field(None, ge=0, le=150)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Settings Example
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        validate_default=True,
        case_sensitive=True
    )

    DATABASE_URL: str
    JWT_SECRET_KEY: str
    DEBUG: bool = False
```

### Advanced Model Example
```python
from pydantic import BaseModel, ConfigDict, Field, computed_field
from typing import List, Optional

class OrderModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        frozen=True
    )

    id: str = Field(..., description="Order unique identifier")
    items: List[str] = Field(..., min_items=1)
    total: float = Field(..., gt=0)
    discount: Optional[float] = Field(0, ge=0, le=1)

    @computed_field
    def final_total(self) -> float:
        return self.total * (1 - self.discount)
```

## Migration Tips

1. **Moving from Pydantic v1**
- Replace `class Config` with `model_config`
- Update validator decorators
- Review field types and validation
- Test all models after migration

2. **Common Migration Issues**
- Config conflicts between old and new style
- Missing type annotations
- Deprecated validator methods
- Field validation changes

## Testing

1. **Model Testing**
- Test model validation
- Test field constraints
- Test computed fields
- Test serialization/deserialization

2. **Settings Testing**
- Test environment variable loading
- Test default values
- Test validation rules
- Test configuration overrides

## Additional Resources

- [Pydantic v2 Documentation](https://docs.pydantic.dev/latest/)
- [Pydantic Settings Management](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Migration Guide](https://docs.pydantic.dev/latest/migration/)
- [API Reference](https://docs.pydantic.dev/latest/api/base_model/)


Pydantic support

Strawberry comes with support for Pydantic . This allows for the creation of Strawberry types from pydantic models without having to write code twice.

Here’s a basic example of how this works, let’s say we have a pydantic Model for a user, like this:

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    signup_ts: Optional[datetime] = None
    friends: List[int] = []


We can create a Strawberry type by using the strawberry.experimental.pydantic.type decorator:

import strawberry

from .models import User


@strawberry.experimental.pydantic.type(model=User)
class UserType:
    id: strawberry.auto
    name: strawberry.auto
    friends: strawberry.auto


The strawberry.experimental.pydantic.type decorator accepts a Pydantic model and wraps a class that contains dataclass style fields with strawberry.auto as the type annotation. The fields marked with strawberry.auto will inherit their types from the Pydantic model.

If you want to include all of the fields from your Pydantic model, you can instead pass all_fields=True to the decorator.

-> Note Care should be taken to avoid accidentally exposing fields that -> weren’t meant to be exposed on an API using this feature.

import strawberry

from .models import User


@strawberry.experimental.pydantic.type(model=User, all_fields=True)
class UserType:
    pass


Input types

Input types are similar to types; we can create one by using the strawberry.experimental.pydantic.input decorator:

import strawberry

from .models import User


@strawberry.experimental.pydantic.input(model=User)
class UserInput:
    id: strawberry.auto
    name: strawberry.auto
    friends: strawberry.auto


Interface types

Interface types are similar to normal types; we can create one by using the strawberry.experimental.pydantic.interface decorator:

import strawberry
from pydantic import BaseModel
from typing import List


# pydantic types
class User(BaseModel):
    id: int
    name: str


class NormalUser(User):
    friends: List[int] = []


class AdminUser(User):
    role: int


# strawberry types
@strawberry.experimental.pydantic.interface(model=User)
class UserType:
    id: strawberry.auto
    name: strawberry.auto


@strawberry.experimental.pydantic.type(model=NormalUser)
class NormalUserType(UserType):  # note the base class
    friends: strawberry.auto


@strawberry.experimental.pydantic.type(model=AdminUser)
class AdminUserType(UserType):
    role: strawberry.auto


Error Types

In addition to object types and input types, Strawberry allows you to create “error types”. You can use these error types to have a typed representation of Pydantic errors in GraphQL. Let’s see an example:

from pydantic import BaseModel, constr
import strawberry


class User(BaseModel):
    id: int
    name: constr(min_length=2)
    signup_ts: Optional[datetime] = None
    friends: List[int] = []


@strawberry.experimental.pydantic.error_type(model=User)
class UserError:
    id: strawberry.auto
    name: strawberry.auto
    friends: strawberry.auto


type UserError {
  id: [String!]
  name: [String!]
  friends: [[String!]]
}


where each field will hold a list of error messages
Extending types

You can use the usual Strawberry syntax to add additional new fields to the GraphQL type that aren’t defined in the pydantic model

import strawberry
from pydantic import BaseModel

from .models import User


class User(BaseModel):
    id: int
    name: str


@strawberry.experimental.pydantic.type(model=User)
class User:
    id: strawberry.auto
    name: strawberry.auto
    age: int


type User {
  id: Int!
  name: String!
  age: Int!
}


Converting types

The generated types won’t run any pydantic validation. This is to prevent confusion when extending types and also to be able to run validation exactly where it is needed.

To convert a Pydantic instance to a Strawberry instance you can use from_pydantic on the Strawberry type:

import strawberry
from typing import List, Optional
from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str


@strawberry.experimental.pydantic.type(model=User)
class UserType:
    id: strawberry.auto
    name: strawberry.auto


instance = User(id="123", name="Jake")

data = UserType.from_pydantic(instance)


If your Strawberry type includes additional fields that aren’t defined in the pydantic model, you will need to use the extra parameter of from_pydantic to specify the values to assign to them.

import strawberry
from typing import List, Optional
from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str


@strawberry.experimental.pydantic.type(model=User)
class UserType:
    id: strawberry.auto
    name: strawberry.auto
    age: int


instance = User(id="123", name="Jake")

data = UserType.from_pydantic(instance, extra={"age": 10})


The data dictionary structure follows the structure of your data — if you have a list of User , you should send an extra that is the list of User with the missing data (in this case, age ).

You don’t need to send all fields; data from the model is used first and then the extra parameter is used to fill in any additional missing data.

To convert a Strawberry instance to a pydantic instance and trigger validation, you can use to_pydantic on the Strawberry instance:

import strawberry
from typing import List, Optional
from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str


@strawberry.experimental.pydantic.input(model=User)
class UserInput:
    id: strawberry.auto
    name: strawberry.auto


input_data = UserInput(id="abc", name="Jake")

# this will run pydantic's validation
instance = input_data.to_pydantic()


Constrained types

Strawberry supports pydantic constrained types . Note that constraint is not enforced in the graphql type. Thus, we recommend always working on the pydantic type such that the validation is enforced.

from pydantic import BaseModel, conlist
import strawberry


class Example(BaseModel):
    friends: conlist(str, min_items=1)


@strawberry.experimental.pydantic.input(model=Example, all_fields=True)
class ExampleGQL: ...


@strawberry.type
class Query:
    @strawberry.field()
    def test(self, example: ExampleGQL) -> None:
        # friends may be an empty list here
        print(example.friends)
        # calling to_pydantic() runs the validation and raises
        # an error if friends is empty
        print(example.to_pydantic().friends)


schema = strawberry.Schema(query=Query)


input ExampleGQL {
  friends: [String!]!
}

type Query {
  test(example: ExampleGQL!): Void
}


Classes with __get_validators__

Pydantic BaseModels may define a custom type with __get_validators__ logic. You will need to add a scalar type and add the mapping to the scalar_overrides argument in the Schema class.

import strawberry
from pydantic import BaseModel


class MyCustomType:
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        return MyCustomType()


class Example(BaseModel):
    custom: MyCustomType


@strawberry.experimental.pydantic.type(model=Example, all_fields=True)
class ExampleGQL: ...


MyScalarType = strawberry.scalar(
    MyCustomType,
    # or another function describing how to represent MyCustomType in the response
    serialize=str,
    parse_value=lambda v: MyCustomType(),
)


@strawberry.type
class Query:
    @strawberry.field()
    def test(self) -> ExampleGQL:
        return Example(custom=MyCustomType())


# Tells strawberry to convert MyCustomType into MyScalarType
schema = strawberry.Schema(query=Query, scalar_overrides={MyCustomType: MyScalarType})


Custom Conversion Logic

Sometimes you might not want to translate your Pydantic model into Strawberry using the logic provided in the library. Sometimes types in Pydantic are unrepresentable in GraphQL (such as unions of scalar values) or structural changes are needed before the data is exposed in the schema. In these cases, there are two methods you can use to control the conversion logic more directly.

First, you can use a different type annotation in your Strawberry model for a field type instead of using strawberry.auto to choose an equivalent type. This allows you to do things like converting values to custom scalar types or converting between basic types. Strawberry will call the constructor of the new type annotation with the field value as input, so this only works when conversion is possible through a constructor.

import base64
import strawberry
from pydantic import BaseModel
from typing import Union, NewType


class User(BaseModel):
    id: Union[int, str]  # Not representable in GraphQL
    hash: bytes


Base64 = strawberry.scalar(
    NewType("Base64", bytes),
    serialize=lambda v: base64.b64encode(v).decode("utf-8"),
    parse_value=lambda v: base64.b64decode(v.encode("utf-8")),
)


@strawberry.experimental.pydantic.type(model=User)
class UserType:
    id: str  # Serialize int values to strings
    hash: Base64  # Use a custom scalar to serialize values


@strawberry.type
class Query:
    @strawberry.field
    def test() -> UserType:
        return UserType.from_pydantic(User(id=123, hash=b"abcd"))


schema = strawberry.Schema(query=Query)

print(schema.execute_sync("query { test { id, hash } }").data)
# {"test": {"id": "123", "hash": "YWJjZA=="}}


The other, more comprehensive, method for modifying the conversion logic is to provide custom implementations of from_pydantic and to_pydantic . This allows you full control over the conversion process and bypasses Strawberry’s built in conversion rules completely, while still registering the new type as a Pydantic conversion type so it can be referenced in other models.

This is useful when you need to represent structures that are very different from GraphQL standards, without changing the underlying Pydantic model. An example would be a use case that uses a dict field to store some semi-structured content, which is difficult to represent in GraphQL’s strict type system.

import enum
import dataclasses
import strawberry
from pydantic import BaseModel
from typing import Any, Dict, Optional


class ContentType(enum.Enum):
    NAME = "name"
    DESCRIPTION = "description"


class User(BaseModel):
    id: str
    content: Dict[ContentType, str]


@strawberry.experimental.pydantic.type(model=User)
class UserType:
    id: strawberry.auto
    # Flatten the content dict into specific fields in the query
    content_name: Optional[str] = None
    content_description: Optional[str] = None

    @staticmethod
    def from_pydantic(instance: User, extra: Dict[str, Any] = None) -> "UserType":
        data = instance.dict()
        content = data.pop("content")
        data.update({f"content_{k.value}": v for k, v in content.items()})
        return UserType(**data)

    def to_pydantic(self) -> User:
        data = dataclasses.asdict(self)

        # Pull out the content_* fields into a dict
        content = {}
        for enum_member in ContentType:
            key = f"content_{enum_member.value}"
            if data.get(key) is not None:
                content[enum_member.value] = data.pop(key)
        return User(content=content, **data)


user = User(id="abc", content={ContentType.NAME: "Bob"})
print(UserType.from_pydantic(user))
# UserType(id='abc', content_name='Bob', content_description=None)

user_type = UserType(id="abc", content_name="Bob", content_description=None)
print(user_type.to_pydantic())
# id='abc' content={<ContentType.NAME: 'name'>: 'Bob'}
  