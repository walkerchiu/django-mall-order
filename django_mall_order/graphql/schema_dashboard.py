import graphene

from django_mall_order.graphql.dashboard.order import OrderQuery
from django_mall_order.graphql.dashboard.order_line_item import OrderLineItemQuery


class Mutation(
    graphene.ObjectType,
):
    pass


class Query(
    OrderQuery,
    OrderLineItemQuery,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(mutation=Mutation, query=Query)
