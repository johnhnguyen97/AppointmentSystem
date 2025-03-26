Getting started with Strawberry

This tutorial will help you:

    Obtain a basic understanding of GraphQL principles
    Define a GraphQL schema using Strawberry
    Run the Strawberry server that lets you execute queries against your schema

This tutorial assumes that you are familiar with the command line and Python, and that you have a recent version of Python (3.9+) installed.

Strawberry is built on top of Python's dataclasses and type hints functionality.

Quick Start

In this Quick-Start, we will:

    Set up a basic pair of models with a relation between them.
    Add them to a graphql schema and serve the graph API.
    Query the graph API for model contents.

For a more advanced example of a similar setup including a set of mutations and more queries, please check the example app.

Installation
Terminal window

poetry add strawberry-graphql-django
poetry add django-choices-field  # Not required but recommended

(Not using poetry yet? pip install strawberry-graphql-django works fine too.)

Define your application models

We'll build an example database of fruit and their colours.

Tip

You'll notice that for Fruit.category, we use TextChoicesField instead of TextField(choices=...). This allows strawberry-django to automatically use an enum in the graphQL schema, instead of a string which would be the default behaviour for TextField.

See the choices-field integration for more information.

models.py

from django.db import models
from django_choices_field import TextChoicesField

class FruitCategory(models.TextChoices):
    CITRUS = "citrus", "Citrus"
    BERRY = "berry", "Berry"

class Fruit(models.Model):
    """A tasty treat"""

    name = models.CharField(max_length=20, help_text="The name of the fruit variety")
    category = TextChoicesField(choices_enum=FruitCategory, help_text="The category of the fruit")
    color = models.ForeignKey(
        "Color",
        on_delete=models.CASCADE,
        related_name="fruits",
        blank=True,
        null=True,
        help_text="The color of this kind of fruit",
    )

class Color(models.Model):
    """The hue of your tasty treat"""

    name = models.CharField(
        max_length=20,
        help_text="The color name",
    )

You'll need to make migrations then migrate:
Terminal window

python manage.py makemigrations
python manage.py migrate

Now use the django shell, the admin, the loaddata command or whatever tool you like to load some fruits and colors. I've loaded a red strawberry (predictable, right?!) ready for later.

Define types

Before creating queries, you have to define a type for each model. A type is a fundamental unit of the schema which describes the shape of the data that can be queried from the GraphQL server. Types can represent scalar values (like String, Int, Boolean, Float, and ID), enums, or complex objects that consist of many fields.

Tip

A key feature of strawberry-graphql-django is that it provides helpers to create types from django models, by automatically inferring types (and even documentation!!) from the model fields.

See the fields guide for more information.

types.py

import strawberry_django
from strawberry import auto

from . import models

@strawberry_django.type(models.Fruit)
class Fruit:
    id: auto
    name: auto
    category: auto
    color: "Color"  # Strawberry will understand that this refers to the "Color" type that's defined below

@strawberry_django.type(models.Color)
class Color:
    id: auto
    name: auto
    fruits: list[Fruit] # This tells strawberry about the ForeignKey to the Fruit model and how to represent the Fruit instances on that relation

Build the queries and schema

Next we want to assemble the schema from its building block types.

Warning

You'll notice a familiar statement, fruits: list[Fruit]. We already used this statement in the previous step in types.py. Seeing it twice can be a point of confusion when you're first getting to grips with graph and strawberry.

The purpose here is similar but subtly different. Previously, the syntax defined that it was possible to make a query that traverses within the graph, from a Color to a list of Fruits. Here, the usage defines a root query (a bit like an entrypoint into the graph).

Tip

We add the DjangoOptimizerExtension here. Don't worry about why for now, but you're almost certain to want it.

See the optimizer guide for more information.

schema.py

import strawberry
from strawberry_django.optimizer import DjangoOptimizerExtension

from .types import Fruit

@strawberry.type
class Query:
    fruits: list[Fruit] = strawberry_django.field()

schema = strawberry.Schema(
    query=Query,
    extensions=[
        DjangoOptimizerExtension,
    ],
)

Serving the API

Now we're showing off. This isn't enabled by default, since existing django applications will likely have model docstrings and help text that aren't user-oriented. But if you're starting clean (or overhauling existing dosctrings and helptext), setting up the following is super useful for your API users.

If you don't set these true, you can always provide user-oriented descriptions. See the

settings.py

STRAWBERRY_DJANGO = {
    "FIELD_DESCRIPTION_FROM_HELP_TEXT": True,
    "TYPE_DESCRIPTION_FROM_MODEL_DOCSTRING": True,
}

urls.py

from django.urls import include, path
from strawberry.django.views import AsyncGraphQLView

from .schema import schema

urlpatterns = [
    path('graphql', AsyncGraphQLView.as_view(schema=schema)),
]

This generates following schema:

schema.graphql

enum FruitCategory {
  CITRUS
  BERRY
}

"""
A tasty treat
"""
type Fruit {
  id: ID!
  name: String!
  category: FruitCategory!
  color: Color
}

type Color {
  id: ID!
  """
  field description
  """
  name: String!
  fruits: [Fruit!]
}

type Query {
  fruits: [Fruit!]!
}

Using the API

Start your server with:
Terminal window

python manage.py runserver

Then visit localhost:8000/graphql in your browser. You should see the graphql explorer being served by django. Using the interactive query tool, you can query for the fruits you added earlier:

GraphiQL with fruit

Step 1: Create a new project and install Strawberry

Let’s create a new folder:
Terminal window

mkdir strawberry-demo
cd strawberry-demo


After that we need a new virtualenv:
Terminal window

python -m venv virtualenv


Activate the virtualenv and then install strawberry plus the debug server.
Terminal window

source virtualenv/bin/activate
pip install 'strawberry-graphql[debug-server]'


  Step 2: Define the schema

Every GraphQL server uses a schema to define the structure of the data that clients can query. In this example, we will create a server for querying a collection of books by title and author.

In your favorite editor create a file called schema.py , with the following contents:

import typing
import strawberry


@strawberry.type
class Book:
    title: str
    author: str


@strawberry.type
class Query:
    books: typing.List[Book]


This will create a GraphQL schema where clients will be able to execute a query named books that will return a list of zero or more books.


tep 3: Define your data set

Now that we have our structure of your schema, we can define the data itself. Strawberry can work with any data source (for example a database, a REST API, files, etc). For this tutorial we will be using hard-coded data.

Let’s create a function that returns some books.

def get_books():
    return [
        Book(
            title="The Great Gatsby",
            author="F. Scott Fitzgerald",
        ),
    ]


Since strawberry makes uses of python classes to create the schema, this means that we can also reuse them to create the data objects.


Step 4: Define a resolver

We now have a function that returns some books, but Strawberry doesn’t know it should use it when executing a query. To fix this we need to update our query to specify the resolver for our books. A resolver tells Strawberry how to fetch the data associated with a particular field.

Let’s update our Query:

@strawberry.type
class Query:
    books: typing.List[Book] = strawberry.field(resolver=get_books)


Using strawberry.field allows us to specify a resolver for a particular field.


Note

We didn’t have to specify any resolver for the Book’s fields, this is because Strawberry adds a default for each field, returning the value of that field.

Step 5: Create our schema and run it

We have defined our data and query, now what we need to do is create a GraphQL schema and start the server.

To create the schema add the following code:

schema = strawberry.Schema(query=Query)


Then run the following command
Terminal window

strawberry server schema


This will start a debug server, you should see the following output:

Running strawberry on http://0.0.0.0:8000/graphql 🍓

  Step 6: execute your first query

We can now execute GraphQL queries. Strawberry comes with a tool called GraphiQL. To open it go to http://0.0.0.0:8000/graphql

You should see something like this:

![alt text](index-server.vEXctPmd_ZYfLjO.webp)

he GraphiQL UI includes:

    A text area (to the left) for writing queries
    A Play button (the triangle button in the middle) for executing queries
    A text area (to the right) for viewing query results Views for schema inspection and generated documentation (via tabs on the right side)

Our server supports a single query named books. Let’s execute it!

Paste the following string into the left area and then click the play button:

{
  books {
    title
    author
  }
}


You should see the hardcoded data appear on the right side:

![alt text](index-query-example.apr0tLHb_2pxEMp.webp)


Schema basics

GraphQL servers use a schema to describe the shape of the data. The schema defines a hierarchy of types with fields that are populated from data stores. The schema also specifies exactly which queries and mutations are available for clients to execute.

This guide describes the basic building blocks of a schema and how to use Strawberry to create one.
Schema definition language (SDL)

There are two approaches for creating the schema for a GraphQL server. One is called “schema-first” and the other is called “code-first”. Strawberry only supports code-first schemas. Before diving into code-first, let’s first explain what the Schema definition language is.

Schema first works using the Schema Definition Language of GraphQL, which is included in the GraphQL spec.

Here’s an example of schema defined using the SDL:

type Book {
  title: String!
  author: Author!
}

type Author {
  name: String!
  books: [Book!]!
}


The schema defines all the types and relationships between them. With this we enable client developers to see exactly what data is available and request a specific subset of that data.
Note

The ! sign specifies that a field is non-nullable.

Notice that the schema doesn’t specify how to get the data. That comes later when defining the resolvers.
Code first approach

As mentioned Strawberry uses a code first approach. The previous schema would look like this in Strawberry

import typing
import strawberry


@strawberry.type
class Book:
    title: str
    author: "Author"


@strawberry.type
class Author:
    name: str
    books: typing.List[Book]


As you can see the code maps almost one to one with the schema, thanks to python’s type hints feature.

Notice that here we are also not specifying how to fetch data, that will be explained in the resolvers section.
Supported types

GraphQL supports a few different types:

    Scalar types
    Object types
    The Query type
    The Mutation type
    Input types

Scalar types

Scalar types are similar to Python primitive types. Here’s the list of the default scalar types in GraphQL:

    Int, a signed 32-bit integer, maps to python’s int
    Float, a signed double-precision floating-point value, maps to python’s float
    String, maps to python’s str
    Boolean, true or false, maps to python’s bool
    ID, a unique identifier that usually used to refetch an object or as the key for a cache. Serialized as string and available as strawberry.ID(“value”)
    UUID , a UUID value serialized as a string

Note

Strawberry also includes support for date, time and datetime objects, they are not officially included with the GraphQL spec, but they are usually needed in most servers. They are serialized as ISO-8601.

These primitives work for the majority of use cases, but you can also specify your own scalar types .
Object types

Most of the types you define in a GraphQL schema are object types. An object type contains a collection of fields, each of which can be either a scalar type or another object type.

Object types can refer to each other, as we had in our schema earlier:

import typing
import strawberry


@strawberry.type
class Book:
    title: str
    author: "Author"


@strawberry.type
class Author:
    name: str
    books: typing.List[Book]


Providing data to fields

In the above schema, a Book has an author field and an Author has a books field, yet we do not know how our data can be mapped to fulfil the structure of the promised schema.

To achieve this, we introduce the concept of the resolver that provides some data to a field through a function.

Continuing with this example of books and authors, resolvers can be defined to provide values to the fields:

def get_author_for_book(root) -> "Author":
    return Author(name="Michael Crichton")


@strawberry.type
class Book:
    title: str
    author: "Author" = strawberry.field(resolver=get_author_for_book)


def get_books_for_author(root) -> typing.List[Book]:
    return [Book(title="Jurassic Park")]


@strawberry.type
class Author:
    name: str
    books: typing.List[Book] = strawberry.field(resolver=get_books_for_author)


def get_authors(root) -> typing.List[Author]:
    return [Author(name="Michael Crichton")]


@strawberry.type
class Query:
    authors: typing.List[Author] = strawberry.field(resolver=get_authors)
    books: typing.List[Book] = strawberry.field(resolver=get_books_for_author)


These functions provide the strawberry.field with the ability to render data to the GraphQL query upon request and are the backbone of all GraphQL APIs.

This example is trivial since the resolved data is entirely static. However, when building more complex APIs, these resolvers can be written to map data from databases, e.g. making SQL queries using SQLAlchemy, and other APIs, e.g. making HTTP requests using aiohttp.

For more information and detail on the different ways to write resolvers, see the resolvers section .
The Query type

The Query type defines exactly which GraphQL queries (i.e., read operations) clients can execute against your data. It resembles an object type, but its name is always Query .

Each field of the Query type defines the name and return type of a different supported query. The Query type for our example schema might resemble the following:

@strawberry.type
class Query:
    books: typing.List[Book]
    authors: typing.List[Author]


This Query type defines two available queries: books and authors. Each query returns a list of the corresponding type.

With a REST-based API, books and authors would probably be returned by different endpoints (e.g., /api/books and /api/authors). The flexibility of GraphQL enables clients to query both resources with a single request.
Structuring a query

When your clients build queries to execute against your data graph, those queries match the shape of the object types you define in your schema.

Based on our example schema so far, a client could execute the following query, which requests both a list of all book titles and a list of all author names:

query {
  books {
    title
  }

  authors {
    name
  }
}


Our server would then respond to the query with results that match the query’s structure, like so:

{
  "data": {
    "books": [{ "title": "Jurassic Park" }],
    "authors": [{ "name": "Michael Crichton" }]
  }
}


Although it might be useful in some cases to fetch these two separate lists, a client would probably prefer to fetch a single list of books, where each book’s author is included in the result.

Because our schema’s Book type has an author field of type Author, a client could structure their query like so:

query {
  books {
    title
    author {
      name
    }
  }
}


And once again, our server would respond with results that match the query’s structure:

{
  "data": {
    "books": [
      { "title": "Jurassic Park", "author": { "name": "Michael Crichton" } }
    ]
  }
}


The Mutation type

The Mutation type is similar in structure and purpose to the Query type. Whereas the Query type defines your data’s supported read operations, the Mutation type defines supported write operations.

Each field of the Mutation type defines the signature and return type of a different mutation. The Mutation type for our example schema might resemble the following:

@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_book(self, title: str, author: str) -> Book: ...


This Mutation type defines a single available mutation, addBook . The mutation accepts two arguments (title and author) and returns a newly created Book object. As you’d expect, this Book object conforms to the structure that we defined in our schema.
Note

Strawberry converts fields names from snake case to camel case by default. This can be changed by specifying a custom StrawberryConfig on the schema

Structuring a mutation

Like queries, mutations match the structure of your schema’s type definitions. The following mutation creates a new Book and requests certain fields of the created object as a return value:

mutation {
  addBook(title: "Fox in Socks", author: "Dr. Seuss") {
    title
    author {
      name
    }
  }
}


As with queries, our server would respond to this mutation with a result that matches the mutation’s structure, like so:

{
  "data": {
    "addBook": {
      "title": "Fox in Socks",
      "author": {
        "name": "Dr. Seuss"
      }
    }
  }
}


Input types

Input types are special object types that allow you to pass objects as arguments to queries and mutations (as opposed to passing only scalar types). Input types help keep operation signatures clean.

Consider our previous mutation to add a book:

@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_book(self, title: str, author: str) -> Book: ...


Instead of accepting two arguments, this mutation could accept a single input type that includes all of these fields. This comes in extra handy if we decide to accept an additional argument in the future, such as a publication date.

An input type’s definition is similar to an object type’s, but it uses the input keyword:

@strawberry.input
class AddBookInput:
    title: str
    author: str


@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_book(self, book: AddBookInput) -> Book: ...


Not only does this facilitate passing the AddBookInput type around within our schema, it also provides a basis for annotating fields with descriptions that are automatically exposed by GraphQL-enabled tools:

@strawberry.input
class AddBookInput:
    title: str = strawberry.field(description="The title of the book")
    author: str = strawberry.field(description="The name of the author")


Input types can sometimes be useful when multiple operations require the exact same set of information, but you should reuse them sparingly. Operations might eventually diverge in their sets of required arguments.


Queries

In GraphQL you use queries to fetch data from a server. In Strawberry you can define the data your server provides by defining query types.

By default all the fields the API exposes are nested under a root Query type.

This is how you define a root query type in Strawberry:

@strawberry.type
class Query:
    name: str


schema = strawberry.Schema(query=Query)


This creates a schema where the root type Query has one single field called name.

As you notice we don’t provide a way to fetch data. In order to do so we need to provide a resolver , a function that knows how to fetch data for a specific field.

For example in this case we could have a function that always returns the same name:

def get_name() -> str:
    return "Strawberry"


@strawberry.type
class Query:
    name: str = strawberry.field(resolver=get_name)


schema = strawberry.Schema(query=Query)


So now, when requesting the name field, the get_name function will be called.

Alternatively a field can be declared using a decorator:

@strawberry.type
class Query:
    @strawberry.field
    def name(self) -> str:
        return "Strawberry"


The decorator syntax supports specifying a graphql_type for cases when the return type of the function does not match the GraphQL type:

class User:
    id: str
    name: str

    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

@strawberry.type(name="User")
class UserType:
    id: strawberry.ID
    name: str

@strawberry.type
class Query:
    @strawberry.field(graphql_type=UserType)
    def user(self) -> User
        return User(id="ringo", name="Ringo")


Arguments

GraphQL fields can accept arguments, usually to filter out or retrieve specific objects:

FRUITS = [
    "Strawberry",
    "Apple",
    "Orange",
]


@strawberry.type
class Query:
    @strawberry.field
    def fruit(self, startswith: str) -> str | None:
        for fruit in FRUITS:
            if fruit.startswith(startswith):
                return fruit
        return None

  Mutations

As opposed to queries, mutations in GraphQL represent operations that modify server-side data and/or cause side effects on the server. For example, you can have a mutation that creates a new instance in your application or a mutation that sends an email. Like in queries, they accept parameters and can return anything a regular field can, including new types and existing object types. This can be useful for fetching the new state of an object after an update.

Let’s improve our books project from the Getting started tutorial and implement a mutation that is supposed to add a book:

import strawberry


# Reader, you can safely ignore Query in this example, it is required by
# strawberry.Schema so it is included here for completeness
@strawberry.type
class Query:
    @strawberry.field
    def hello() -> str:
        return "world"


@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_book(self, title: str, author: str) -> Book:
        print(f"Adding {title} by {author}")

        return Book(title=title, author=author)


schema = strawberry.Schema(query=Query, mutation=Mutation)


Like queries, mutations are defined in a class that is then passed to the Schema function. Here we create an addBook mutation that accepts a title and an author and returns a Book type.

We would send the following GraphQL document to our server to execute the mutation:

mutation {
  addBook(title: "The Little Prince", author: "Antoine de Saint-Exupéry") {
    title
  }
}


The addBook mutation is a simplified example. In a real-world application mutations will often need to handle errors and communicate those errors back to the client. For example we might want to return an error if the book already exists.

You can checkout our documentation on dealing with errors to learn how to return a union of types from a mutation.
Mutations without returned data

It is also possible to write a mutation that doesn’t return anything.

This is mapped to a Void GraphQL scalar, and always returns null

@strawberry.type
class Mutation:
    @strawberry.mutation
    def restart() -> None:
        print(f"Restarting the server")


type Mutation {
  restart: Void
}


Note

Mutations with void-result go against this community-created guide on GQL best practices .

The input mutation extension

It is usually useful to use a pattern of defining a mutation that receives a single input type argument called input .

Strawberry provides a helper to create a mutation that automatically creates an input type for you, whose attributes are the same as the args in the resolver.

For example, suppose we want the mutation defined in the section above to be an input mutation. We can add the InputMutationExtension to the field like this:

from strawberry.field_extensions import InputMutationExtension


@strawberry.type
class Mutation:
    @strawberry.mutation(extensions=[InputMutationExtension()])
    def update_fruit_weight(
        self,
        info: strawberry.Info,
        id: strawberry.ID,
        weight: Annotated[
            float,
            strawberry.argument(description="The fruit's new weight in grams"),
        ],
    ) -> Fruit:
        fruit = ...  # retrieve the fruit with the given ID
        fruit.weight = weight
        ...  # maybe save the fruit in the database
        return fruit


That would generate a schema like this:

input UpdateFruitWeightInput {
  id: ID!

  """
  The fruit's new weight in grams
  """
  weight: Float!
}

type Mutation {
  updateFruitWeight(input: UpdateFruitWeightInput!): Fruit!
}


Nested mutations

To avoid a graph becoming too large and to improve discoverability, it can be helpful to group mutations in a namespace, as described by Apollo’s guide on Namespacing by separation of concerns .

type Mutation {
  fruit: FruitMutations!
}

type FruitMutations {
  add(input: AddFruitInput): Fruit!
  updateWeight(input: UpdateFruitWeightInput!): Fruit!
}


Since all GraphQL operations are fields, we can define a FruitMutation type and add mutation fields to it like we could add mutation fields to the root Mutation type.

import strawberry


@strawberry.type
class FruitMutations:
    @strawberry.mutation
    def add(self, info, input: AddFruitInput) -> Fruit: ...

    @strawberry.mutation
    def update_weight(self, info, input: UpdateFruitWeightInput) -> Fruit: ...


@strawberry.type
class Mutation:
    @strawberry.field
    def fruit(self) -> FruitMutations:
        return FruitMutations()


Note

Fields on the root Mutation type are resolved serially. Namespace types introduce the potential for mutations to be resolved asynchronously and in parallel because the mutation fields that mutate data are no longer at the root level.

To guarantee serial execution when namespace types are used, clients should use aliases to select the root mutation field for each mutation. In the following example, once addFruit execution is complete, updateFruitWeight begins.

mutation (
  $addFruitInput: AddFruitInput!
  $updateFruitWeightInput: UpdateFruitWeightInput!
) {
  addFruit: fruit {
    add(input: $addFruitInput) {
      id
    }
  }

  updateFruitWeight: fruit {
    updateWeight(input: $updateFruitWeightInput) {
      id
    }
  }
}


For more details, see Apollo’s guide on Namespaces for serial mutations and Rapid API’s Interactive Guide to GraphQL Queries: Aliases and Variables .


Subscriptions

In GraphQL you can use subscriptions to stream data from a server. To enable this with Strawberry your server must support ASGI and websockets or use the AIOHTTP integration.

This is how you define a subscription-capable resolver:

import asyncio
from typing import AsyncGenerator

import strawberry


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "world"


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def count(self, target: int = 100) -> AsyncGenerator[int, None]:
        for i in range(target):
            yield i
            await asyncio.sleep(0.5)


schema = strawberry.Schema(query=Query, subscription=Subscription)


Like queries and mutations, subscriptions are defined in a class and passed to the Schema function. Here we create a rudimentary counting function which counts from 0 to the target sleeping between each loop iteration.
Note

The return type of count is AsyncGenerator where the first generic argument is the actual type of the response, in most cases the second argument should be left as None (more about Generator typing here ).

We would send the following GraphQL document to our server to subscribe to this data stream:

subscription {
  count(target: 5)
}
  ![alt text](subscriptions-count-websocket.D5io8Aym_1ByWbb.webp)

Authenticating Subscriptions

Without going into detail on why , custom headers cannot be set on websocket requests that originate in browsers. Therefore, when making any GraphQL requests that rely on a websocket connection, header-based authentication is impossible.

Other popular GraphQL solutions, like Apollo for example, implement functionality to pass information from the client to the server at the point of websocket connection initialisation. In this way, information that is relevant to the websocket connection initialisation and to the lifetime of the connection overall can be passed to the server before any data is streamed back by the server. As such, it is not limited to only authentication credentials!

Strawberry’s implementation follows that of Apollo’s, which as documentation for client and server implementations, by reading the contents of the initial websocket connection message into the info.context object.

With Apollo-client as an example of how to send this initial connection information, one defines a ws-link as:

import { GraphQLWsLink } from "@apollo/client/link/subscriptions";
import { createClient } from "graphql-ws";

const wsLink = new GraphQLWsLink(
  createClient({
    url: "ws://localhost:4000/subscriptions",
    connectionParams: {
      authToken: "Bearer I_AM_A_VALID_AUTH_TOKEN",
    },
  }),
);


and then, upon the establishment of the Susbcription request and underlying websocket connection, Strawberry injects this connectionParams object as follows:

import asyncio
from typing import AsyncGenerator

import strawberry

from .auth import authenticate_token


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "world"


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def count(
        self, info: strawberry.Info, target: int = 100
    ) -> AsyncGenerator[int, None]:
        connection_params: dict = info.context.get("connection_params")
        token: str = connection_params.get(
            "authToken"
        )  # equal to "Bearer I_AM_A_VALID_AUTH_TOKEN"
        if not authenticate_token(token):
            raise Exception("Forbidden!")
        for i in range(target):
            yield i
            await asyncio.sleep(0.5)


schema = strawberry.Schema(query=Query, subscription=Subscription)


Strawberry expects the connection_params object to be any type, so the client is free to send any valid JSON object as the initial message of the websocket connection, which is abstracted as connectionParams in Apollo-client, and it will be successfully injected into the info.context object. It is then up to you to handle it correctly!
Advanced Subscription Patterns

Typically a GraphQL subscription is streaming something more interesting back. With that in mind your subscription function can return one of:

    AsyncIterator , or
    AsyncGenerator

Both of these types are documented in PEP-525 . Anything yielded from these types of resolvers will be shipped across the websocket. Care needs to be taken to ensure the returned values conform to the GraphQL schema.

The benefit of an AsyncGenerator, over an iterator, is that the complex business logic can be broken out into a separate module within your codebase. Allowing you to keep the resolver logic succinct.

The following example is similar to the one above, except it returns an AsyncGenerator to the ASGI server which is responsible for streaming subscription results until the Generator exits.

import strawberry
import asyncio
import asyncio.subprocess as subprocess
from asyncio import streams
from typing import Any, AsyncGenerator, AsyncIterator, Coroutine, Optional


async def wait_for_call(coro: Coroutine[Any, Any, bytes]) -> Optional[bytes]:
    """
    wait_for_call calls the supplied coroutine in a wait_for block.

    This mitigates cases where the coroutine doesn't yield until it has
    completed its task. In this case, reading a line from a StreamReader; if
    there are no `\n` line chars in the stream the function will never exit
    """
    try:
        return await asyncio.wait_for(coro(), timeout=0.1)
    except asyncio.TimeoutError:
        pass


async def lines(stream: streams.StreamReader) -> AsyncIterator[str]:
    """
    lines reads all lines from the provided stream, decoding them as UTF-8
    strings.
    """
    while True:
        b = await wait_for_call(stream.readline)
        if b:
            yield b.decode("UTF-8").rstrip()
        else:
            break


async def exec_proc(target: int) -> subprocess.Process:
    """
    exec_proc starts a sub process and returns the handle to it.
    """
    return await asyncio.create_subprocess_exec(
        "/bin/bash",
        "-c",
        f"for ((i = 0 ; i < {target} ; i++)); do echo $i; sleep 0.2; done",
        stdout=subprocess.PIPE,
    )


async def tail(proc: subprocess.Process) -> AsyncGenerator[str, None]:
    """
    tail reads from stdout until the process finishes
    """
    # Note: race conditions are possible here since we're in a subprocess. In
    # this case the process can finish between the loop predicate and the call
    # to read a line from stdout. This is a good example of why you need to
    # be defensive by using asyncio.wait_for in wait_for_call().
    while proc.returncode is None:
        async for l in lines(proc.stdout):
            yield l
    else:
        # read anything left on the pipe after the process has finished
        async for l in lines(proc.stdout):
            yield l


@strawberry.type
class Query:
    @strawberry.field
    def hello() -> str:
        return "world"


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def run_command(self, target: int = 100) -> AsyncGenerator[str, None]:
        proc = await exec_proc(target)
        return tail(proc)


schema = strawberry.Schema(query=Query, subscription=Subscription)


Unsubscribing subscriptions

In GraphQL, it is possible to unsubscribe from a subscription. Strawberry supports this behaviour, and is done using a try...except block.

In Apollo-client, closing a subscription can be achieved like the following:

const client = useApolloClient();
const subscriber = client.subscribe({query: ...}).subscribe({...})
// ...
// done with subscription. now unsubscribe
subscriber.unsubscribe();


Strawberry can capture when a subscriber unsubscribes using an asyncio.CancelledError exception.

import asyncio
from typing import AsyncGenerator
from uuid import uuid4

import strawberry

# track active subscribers
event_messages = {}


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def message(self) -> AsyncGenerator[int, None]:
        try:
            subscription_id = uuid4()

            event_messages[subscription_id] = []

            while True:
                if len(event_messages[subscription_id]) > 0:
                    yield event_messages[subscription_id]
                    event_messages[subscription_id].clear()

                await asyncio.sleep(1)
        except asyncio.CancelledError:
            # stop listening to events
            del event_messages[subscription_id]


GraphQL over WebSocket protocols

Strawberry support both the legacy graphql-ws and the newer recommended graphql-transport-ws WebSocket sub-protocols.
Note

The graphql-transport-ws protocols repository is called graphql-ws . However, graphql-ws is also the name of the legacy protocol. This documentation always refers to the protocol names.

Note that the graphql-ws sub-protocol is mainly supported for backwards compatibility. Read the graphql-ws-transport protocols announcement to learn more about why the newer protocol is preferred.

Strawberry allows you to choose which protocols you want to accept. All integrations supporting subscriptions can be configured with a list of subscription_protocols to accept. By default, all protocols are accepted.
AIOHTTP

from strawberry.aiohttp.views import GraphQLView
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL
from api.schema import schema


view = GraphQLView(
    schema, subscription_protocols=[GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL]
)


ASGI

from strawberry.asgi import GraphQL
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL
from api.schema import schema


app = GraphQL(
    schema,
    subscription_protocols=[
        GRAPHQL_TRANSPORT_WS_PROTOCOL,
        GRAPHQL_WS_PROTOCOL,
    ],
)


Django + Channels

import os

from django.core.asgi import get_asgi_application
from strawberry.channels import GraphQLProtocolTypeRouter

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django_asgi_app = get_asgi_application()

# Import your Strawberry schema after creating the django ASGI application
# This ensures django.setup() has been called before any ORM models are imported
# for the schema.
from mysite.graphql import schema


application = GraphQLProtocolTypeRouter(
    schema,
    django_application=django_asgi_app,
)


Note: Check the channels integraton page for more information regarding it.
FastAPI

from strawberry.fastapi import GraphQLRouter
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL
from fastapi import FastAPI
from api.schema import schema

graphql_router = GraphQLRouter(
    schema,
    subscription_protocols=[
        GRAPHQL_TRANSPORT_WS_PROTOCOL,
        GRAPHQL_WS_PROTOCOL,
    ],
)
app = FastAPI()
app.include_router(graphql_router, prefix="/graphql")


Single result operations

In addition to streaming operations (i.e. subscriptions), the graphql-transport-ws protocol supports so called single result operations (i.e. queries and mutations).

This enables clients to use one protocol and one connection for queries, mutations and subscriptions. Take a look at the protocols repository to learn how to correctly set up the graphql client of your choice.

Strawberry supports single result operations out of the box when the graphql-transport-ws protocol is enabled. Single result operations are normal queries and mutations, so there is no need to adjust any resolve


Schema codegen

Strawberry supports code generation from SDL files.

Let’s assume we have the following SDL file:

type Query {
  user: User
}

type User {
  id: ID!
  name: String!
}


by running the following command:
Terminal window

strawberry schema-codegen schema.graphql


we’ll get the following output:

import strawberry


@strawberry.type
class Query:
    user: User | None


@strawberry.type
class User:
    id: strawberry.ID
    name: str


schema = strawberry.Schema(query=Query)


  Query codegen

Strawberry supports code generation for GraphQL queries.
Note

Schema codegen will be supported in future releases. We are testing the query codegen in order to come up with a nice API.

Let’s assume we have the following GraphQL schema built with Strawberry:

from typing import List

import strawberry


@strawberry.type
class Post:
    id: strawberry.ID
    title: str


@strawberry.type
class User:
    id: strawberry.ID
    name: str
    email: str

    @strawberry.field
    def post(self) -> Post:
        return Post(id=self.id, title=f"Post for {self.name}")


@strawberry.type
class Query:
    @strawberry.field
    def user(self, info) -> User:
        return User(id=strawberry.ID("1"), name="John", email="abc@bac.com")

    @strawberry.field
    def all_users(self) -> List[User]:
        return [
            User(id=strawberry.ID("1"), name="John", email="abc@bac.com"),
        ]


schema = strawberry.Schema(query=Query)


and we want to generate types based on the following query:

query MyQuery {
  user {
    post {
      title
    }
  }
}


With the following command:
Terminal window

strawberry codegen --schema schema --output-dir ./output -p python query.graphql


We’ll get the following output inside output/query.py :

class MyQueryResultUserPost:
    title: str


class MyQueryResultUser:
    post: MyQueryResultUserPost


class MyQueryResult:
    user: MyQueryResultUser


Why is this useful?

Query code generation is usually used to generate types for clients using your GraphQL APIs.

Tools like GraphQL Codegen exist in order to create types and code for your clients. Strawberry’s codegen feature aims to address the similar problem without needing to install a separate tool.
Plugin system

Strawberry’s codegen supports plugins, in the example above for example, we are using the python plugin. To pass more plugins to the codegen tool, you can use the -p flag, for example:
Terminal window

strawberry codegen --schema schema --output-dir ./output -p python -p typescript query.graphql


the plugin can be specified as a python path.
Custom plugins

The interface for plugins looks like this:

from strawberry.codegen import CodegenPlugin, CodegenFile, CodegenResult
from strawberry.codegen.types import GraphQLType, GraphQLOperation


class QueryCodegenPlugin:
    def __init__(self, query: Path) -> None:
        """Initialize the plugin.

        The singular argument is the path to the file that is being processed by this plugin.
        """
        self.query = query

    def on_start(self) -> None: ...

    def on_end(self, result: CodegenResult) -> None: ...

    def generate_code(
        self, types: List[GraphQLType], operation: GraphQLOperation
    ) -> List[CodegenFile]:
        return []


    on_start is called before the codegen starts.
    on_end is called after the codegen ends and it receives the result of the codegen. You can use this to format code, or add licenses to files and so on.
    generated_code is called when the codegen starts and it receives the types and the operation. You cans use this to generate code for each type and operation.

Console plugin

There is also a plugin that helps to orchestrate the codegen process and notify the user about what the current codegen process is doing.

The interface for the ConsolePlugin looks like:

class ConsolePlugin:
    def __init__(self, output_dir: Path):
        """Initialize the plugin and tell it where the output should be written."""
        ...

    def before_any_start(self) -> None:
        """This method is called before any plugins have been invoked or any queries have been processed."""
        ...

    def after_all_finished(self) -> None:
        """This method is called after the full code generation is complete.

        It can be used to report on all the things that have happened during the codegen.
        """
        ...

    def on_start(self, plugins: Iterable[QueryCodegenPlugin], query: Path) -> None:
        """This method is called before any of the individual plugins have been started."""
        ...

    def on_end(self, result: CodegenResult) -> None:
        """This method typically persists the results from a single query to the output directory."""
        ...
