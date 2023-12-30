from django.core.exceptions import ValidationError

from django_filters import CharFilter, FilterSet, OrderingFilter
from django_prices.models import MoneyField
from graphene import ResolveInfo
from graphene_django import DjangoListField, DjangoObjectType
from graphene_django.converter import convert_django_field
import graphene
import graphene_django_optimizer as gql_optimizer

from django_app_core.relay.connection import ExtendedConnection
from django_app_core.types import Money
from django_mall_order.helpers.order_line_item_helper import OrderLineItemHelper
from django_mall_order.models import OrderLineItem, OrderLineItemTrans


class OrderLineItemType(DjangoObjectType):
    class Meta:
        model = OrderLineItem
        fields = ()


@convert_django_field.register(MoneyField)
def convert_money_field_to_string(field, registry=None):
    return graphene.Field(Money)


class OrderLineItemTransType(DjangoObjectType):
    class Meta:
        model = OrderLineItemTrans
        fields = (
            "language_code",
            "name",
            "selected_option_values",
        )


class OrderLineItemMerchandiseType(DjangoObjectType):
    class Meta:
        model = OrderLineItem
        fields = ()

    serial = graphene.String()
    slug = graphene.String()

    @staticmethod
    def resolve_serial(root: OrderLineItem, info: ResolveInfo):
        return root.variant.product.serial

    @staticmethod
    def resolve_slug(root: OrderLineItem, info: ResolveInfo):
        return root.variant.slug


class OrderLineItemFilter(FilterSet):
    serial = CharFilter(field_name="serial", lookup_expr="exact")

    class Meta:
        model = OrderLineItem
        fields = []

    order_by = OrderingFilter(
        fields=(
            "serial",
            "created_at",
            "updated_at",
        )
    )


class OrderLineItemConnection(graphene.relay.Connection):
    class Meta:
        node = OrderLineItemType


class OrderLineItemNode(gql_optimizer.OptimizedDjangoObjectType):
    class Meta:
        model = OrderLineItem
        exclude = (
            "currency",
            "price",
            "price_amount",
            "price_sale_amount",
            "price_final_amount",
            "cost_total",
            "cost_total_amount",
            "variant",
            "deleted",
            "deleted_by_cascade",
        )
        filterset_class = OrderLineItemFilter
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection

    translations = DjangoListField(OrderLineItemTransType)
    photo_url = graphene.String()
    selected_option_values = graphene.List(graphene.String)

    @classmethod
    def get_queryset(cls, queryset, info: ResolveInfo):
        if info.context.user.is_anonymous:
            raise ValidationError("This operation is not allowed!")

        return (
            queryset.select_related("order", "variant", "variant__product")
            .prefetch_related("translations")
            .filter(order__customer_id=info.context.user.id)
        )

    @classmethod
    def get_node(cls, info: ResolveInfo, id):
        if info.context.user.is_anonymous:
            raise ValidationError("This operation is not allowed!")

        return (
            cls._meta.model.objects.select_related(
                "order", "variant", "variant__product"
            )
            .filter(pk=id, order__customer_id=info.context.user.id)
            .first()
        )

    @staticmethod
    def resolve_translations(root: OrderLineItem, info: ResolveInfo):
        return root.translations

    @staticmethod
    def resolve_photo_url(root: OrderLineItem, info: ResolveInfo):
        order_line_item_helper = OrderLineItemHelper(order_line_item=root)

        return order_line_item_helper.get_photo_url()

    @staticmethod
    def resolve_selected_option_values(root: OrderLineItem, info: ResolveInfo):
        order_line_item_helper = OrderLineItemHelper(order_line_item=root)

        return order_line_item_helper.get_selected_option_values()
