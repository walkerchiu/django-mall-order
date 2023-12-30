from django_filters import CharFilter, DateTimeFilter, FilterSet, OrderingFilter
from graphene import ResolveInfo
from graphene_django import DjangoObjectType
import graphene
import graphene_django_optimizer as gql_optimizer

from django_app_core.filters import CharInFilter
from django_app_core.relay.connection import ExtendedConnection
from django_mall_order.models import Order


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ()


class OrderFilter(FilterSet):
    slug = CharFilter(field_name="slug", lookup_expr="exact")
    status_in = CharInFilter(field_name="checkout__status", lookup_expr="in")
    customer_name = CharFilter(
        field_name="customer__profile__name", lookup_expr="exact"
    )
    customer_email = CharFilter(field_name="customer__email", lookup_expr="exact")
    customer_mobile = CharFilter(
        field_name="customer__profile__mobile", lookup_expr="exact"
    )
    created_at_gt = DateTimeFilter(field_name="created_at", lookup_expr="gt")
    created_at_lt = DateTimeFilter(field_name="created_at", lookup_expr="lt")

    class Meta:
        model = Order
        fields = []

    order_by = OrderingFilter(
        fields=(
            "cost_total_amount",
            "created_at",
            "updated_at",
        )
    )


class OrderConnection(graphene.relay.Connection):
    class Meta:
        node = OrderType


class OrderNode(gql_optimizer.OptimizedDjangoObjectType):
    class Meta:
        model = Order
        exclude = (
            "deleted",
            "deleted_by_cascade",
        )
        filterset_class = OrderFilter
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info: ResolveInfo):
        return queryset.select_related(
            "checkout",
            "checkout__checkoutpayment",
            "checkout__checkoutpayment__payment",
            "checkout__checkoutshipment",
            "checkout__checkoutshipment__shipment",
            "customer",
            "customer__profile",
        ).prefetch_related("orderlineitem_set", "orderlineitem_set__translations")

    @classmethod
    def get_node(cls, info: ResolveInfo, id):
        return (
            cls._meta.model.objects.select_related(
                "checkout",
                "checkout__checkoutpayment",
                "checkout__checkoutpayment__payment",
                "checkout__checkoutshipment",
                "checkout__checkoutshipment__shipment",
                "customer",
                "customer__profile",
            )
            .filter(pk=id)
            .first()
        )