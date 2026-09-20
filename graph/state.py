from typing import TypedDict


class SellerState(TypedDict, total=False):
    photo_url: str          # raw photo, publicly reachable (telegram file link)
    product_name: str
    category: str
    cost_price: int          # harga modal, rupiah

    enhanced_photo_urls: list[bytes]
    competitor_data: str
    price_range: str
    listing_title: str
    listing_description: str
    captions: list[str]
