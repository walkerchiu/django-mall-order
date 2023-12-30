from typing import Tuple
import datetime

from django.db import transaction

from django_app_account.models import User
from django_app_organization.models import Organization
from django_mall_cart.models import Cart
from django_mall_checkout.models import Checkout
from django_mall_order.models import Order, OrderLineItem
from django_mall_product.models import ProductTrans


class OrderService:
    def __init__(self, organization: Organization, customer: User):
        self.organization = organization
        self.customer = customer

    def generate_serial(self) -> str:
        return datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")

    @transaction.atomic
    def create_order(self, checkout: Checkout, cart: Cart) -> Tuple[bool, Order]:
        order = Order.objects.create(
            organization=self.organization,
            customer=self.customer,
            checkout=checkout,
            serial=self.generate_serial(),
        )
        if order:
            cartline_set = cart.cartline_set.all()
            for cartline in cartline_set:
                if cartline.variant.is_visible and cartline.variant.product.is_visible:
                    order_line_item = OrderLineItem.objects.create(
                        order=order,
                        variant=cartline.variant,
                        quantity=cartline.quantity,
                        currency=cartline.variant.currency,
                        price_amount=cartline.variant.price_amount,
                        price_sale_amount=cartline.variant.price_sale_amount,
                        price_final_amount=cartline.variant.price_sale_amount,
                    )

                    default_product_trans = ProductTrans.objects.filter(
                        product=cartline.variant.product,
                        language_code=cart.organization.language_code,
                    ).first()
                    if default_product_trans:
                        selected_option_values = []
                        option_values = cartline.variant.selected_option_values.all()
                        for option_value in option_values:
                            option_value_trans = option_value.translations.filter(
                                language_code=default_product_trans.language_code
                            ).first()
                            if option_value_trans:
                                selected_option_values.append(option_value_trans.name)
                        order_line_item.translations.create(
                            language_code=default_product_trans.language_code,
                            name=default_product_trans.name,
                            selected_option_values=selected_option_values,
                        )

                    customer_product_trans = ProductTrans.objects.filter(
                        product=cartline.variant.product,
                        language_code=cart.customer.profile.language_code,
                    ).first()
                    if customer_product_trans:
                        selected_option_values = []
                        option_values = cartline.variant.selected_option_values.all()
                        for option_value in option_values:
                            option_value_trans = option_value.translations.filter(
                                language_code=customer_product_trans.language_code
                            ).first()
                            if option_value_trans:
                                selected_option_values.append(option_value_trans.name)
                        order_line_item.translations.create(
                            language_code=customer_product_trans.language_code,
                            name=customer_product_trans.name,
                            selected_option_values=selected_option_values,
                        )

                    if order_line_item.price_amount:
                        order_line_item.cost_total_amount = (
                            order_line_item.price_amount * order_line_item.quantity
                        )
                    order_line_item.cost_sale_total_amount = (
                        order_line_item.price_sale_amount * order_line_item.quantity
                    )
                    order_line_item.cost_final_total_amount = (
                        order_line_item.price_final_amount * order_line_item.quantity
                    )
                    order_line_item.save()

            order.cost_sale_amount = 0
            order.cost_final_amount = 0
            orderlineitem_set = order.orderlineitem_set.all()
            for orderlineitem in orderlineitem_set:
                order.cost_sale_amount = order.cost_sale_amount + (
                    0
                    if orderlineitem.price_sale_amount is None
                    else orderlineitem.price_sale_amount * orderlineitem.quantity
                )
                order.cost_final_amount = order.cost_final_amount + (
                    0
                    if orderlineitem.price_final_amount is None
                    else orderlineitem.price_final_amount * orderlineitem.quantity
                )
                order.quantity = order.quantity + orderlineitem.quantity
            order.cost_shipment_amount = order.checkout.checkoutshipment.price_amount
            order.cost_total_amount = (
                order.cost_sale_amount + order.cost_shipment_amount
            )
            order.save()

            return True, order
        return False, None
