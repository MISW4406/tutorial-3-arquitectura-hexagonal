from strawberry.fastapi import GraphQLRouter
from .consultas import Query
from .mutaciones import Mutation
import strawberry

schema = strawberry.Schema(query=Query, mutation=Mutation)
router = GraphQLRouter(schema)