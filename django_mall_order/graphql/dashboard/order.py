import graphene

from django_app_core.relay.connection import DjangoFilterConnectionField
from django_mall_order.graphql.dashboard.types.order import OrderNode


class OrderMutation(graphene.ObjectType):
    pass


class OrderQuery(graphene.ObjectType):
    order = graphene.relay.Node.Field(OrderNode)
    orders = DjangoFilterConnectionField(
        OrderNode,
        orderBy=graphene.List(of_type=graphene.String),
        page_number=graphene.Int(),
        page_size=graphene.Int(),
    )
