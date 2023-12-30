from django.conf import settings
from django.core.cache import cache
from django.core.files.storage import default_storage

from django_mall_order.models import OrderLineItem


class OrderLineItemHelper:
    def __init__(self, order_line_item: OrderLineItem):
        self.order_line_item = order_line_item

    def get_photo_url(self) -> str:
        object = self.order_line_item.variant.product.productphoto_set.filter(
            is_primary=True
        ).first()
        if not object:
            object = (
                self.order_line_item.variant.product.productphoto_set.order_by(
                    "sort_key"
                )
                .order_by("created_at")
                .first()
            )
            if not object:
                return None

        key = (
            str(object.product.shop_id).replace("-", "")
            + "/product/"
            + str(object.product_id).replace("-", "")
            + "/img-"
            + object.s3_key
        )
        url = cache.get(key)
        if url:
            return url
        else:
            if default_storage.exists(object.s3_key):
                url = default_storage.url(object.s3_key)

                cache.set(
                    key,
                    url,
                    int(settings.AWS_QUERYSTRING_EXPIRE) - 600,
                )

                return url

            return None

    def get_selected_option_values(self):
        selected_option_values = []

        option_values = self.order_line_item.variant.selected_option_values.order_by(
            "product_option__sort_key"
        )
        for option_value in option_values:
            trans = option_value.translations.filter(
                language_code=self.order_line_item.variant.product.organization.language_code
            ).first()

            if trans:
                selected_option_values.append(trans.name)

        return selected_option_values
