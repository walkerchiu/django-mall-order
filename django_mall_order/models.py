import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from django_prices.models import MoneyField
from safedelete.models import SOFT_DELETE_CASCADE

from django_app_account.models import User
from django_app_core.models import CommonDateAndSafeDeleteMixin, TranslationModel
from django_app_organization.models import Organization
from django_mall_checkout.models import Checkout
from django_mall_product.models import Variant


class Order(CommonDateAndSafeDeleteMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, models.CASCADE)
    customer = models.ForeignKey(User, models.CASCADE)
    checkout = models.OneToOneField(Checkout, models.CASCADE)
    serial = models.CharField(max_length=20, unique=True, db_index=True)
    currency = models.CharField(
        max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH,
        default=settings.DEFAULT_CURRENCY_CODE,
    )
    cost_sale_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        blank=True,
        null=True,
    )
    cost_sale = MoneyField(amount_field="cost_sale_amount", currency_field="currency")
    cost_final_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        blank=True,
        null=True,
    )
    cost_final = MoneyField(amount_field="cost_final_amount", currency_field="currency")
    cost_shipment_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        blank=True,
        null=True,
    )
    cost_shipment = MoneyField(
        amount_field="cost_shipment_amount", currency_field="currency"
    )
    cost_total_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        blank=True,
        null=True,
    )
    cost_total = MoneyField(amount_field="cost_total_amount", currency_field="currency")
    quantity = models.PositiveSmallIntegerField(default=0)

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = settings.APP_NAME + "_order_order"
        get_latest_by = "updated_at"

    def __str__(self):
        return str(self.id)


class OrderLineItem(CommonDateAndSafeDeleteMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, models.CASCADE)
    variant = models.ForeignKey(Variant, models.CASCADE)
    quantity = models.IntegerField(db_index=True, validators=[MinValueValidator(1)])
    currency = models.CharField(
        max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH,
        default=settings.DEFAULT_CURRENCY_CODE,
    )
    price_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        blank=True,
        null=True,
    )
    price = MoneyField(amount_field="price_amount", currency_field="currency")
    price_sale_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        blank=True,
        null=True,
    )
    price_sale = MoneyField(amount_field="price_sale_amount", currency_field="currency")
    price_final_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        blank=True,
        null=True,
    )
    price_final = MoneyField(
        amount_field="price_final_amount", currency_field="currency"
    )
    cost_total_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        blank=True,
        null=True,
    )
    cost_total = MoneyField(amount_field="cost_total_amount", currency_field="currency")
    cost_sale_total_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        blank=True,
        null=True,
    )
    cost_sale_total = MoneyField(
        amount_field="cost_sale_total_amount", currency_field="currency"
    )
    cost_final_total_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        blank=True,
        null=True,
    )
    cost_final_total = MoneyField(
        amount_field="cost_final_total_amount", currency_field="currency"
    )

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = settings.APP_NAME + "_order_orderlineitem"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    def __str__(self):
        return str(self.id)


class OrderLineItemTrans(CommonDateAndSafeDeleteMixin, TranslationModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_line_item = models.ForeignKey(
        OrderLineItem, related_name="translations", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255, db_index=True)
    selected_option_values = models.TextField(blank=True, null=True)

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = settings.APP_NAME + "_order_orderlineitem_trans"
        get_latest_by = "updated_at"
        index_together = (("language_code", "order_line_item"),)
        ordering = ["language_code"]

    def __str__(self):
        return str(self.id)
