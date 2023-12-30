import graphene

from django_app_core.relay.connection import DjangoFilterConnectionField
from django_mall_order.graphql.storefront.types.order_line_item import OrderLineItemNode


class OrderLineItemMutation(graphene.ObjectType):
    pass


class OrderLineItemQuery(graphene.ObjectType):
    order_line_items = DjangoFilterConnectionField(
        OrderLineItemNode,
        orderBy=graphene.List(of_type=graphene.String),
        page_number=graphene.Int(),
        page_size=graphene.Int(),
    )
