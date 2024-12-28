from pydantic import BaseModel, Field
from enum import Enum


class EventType(str, Enum):
    AdvancedDom = "advanced-dom"
    Custom = "custom"
    Dom = "dom"
    Standard = "standard"


class GenericElement(BaseModel):
    href: str = Field(..., description="The href attribute of an element")

    id: str = Field(..., description="The id attribute of an element")

    name: str = Field(..., description="The name attribute of an element")

    tagName: str = Field(
        ..., description="A string representation of the tag of an element"
    )

    type: str = Field(
        ...,
        description="The type attribute of an element. Often relevant for an input or button element.",
    )

    value: str = Field(
        ...,
        description="The value attribute of an element. Often relevant for an input element.",
    )


class MouseEventData(BaseModel):
    clientX: float = Field(
        ..., description="The X coordinate of the mouse event, relative to the viewport"
    )

    clientY: float = Field(
        ..., description="The Y coordinate of the mouse event, relative to the viewport"
    )

    pageX: float = Field(
        ..., description="The X coordinate of the mouse event, relative to the page"
    )

    pageY: float = Field(
        ..., description="The Y coordinate of the mouse event, relative to the page"
    )

    screenX: float = Field(
        ..., description="The X coordinate of the mouse event, relative to the screen"
    )

    screenY: float = Field(
        ..., description="The Y coordinate of the mouse event, relative to the screen"
    )

    element: GenericElement

    movementX: float

    movementY: float

    offsetX: float

    offsetY: float


class DOMEvent(BaseModel):
    clientId: str = Field(
        ..., description="The client-side ID of the customer, provided by Shopify"
    )
    data: MouseEventData = Field(..., description="Mouse event data object")
    id: str = Field(..., description="The ID of the customer event")
    name: str = Field(..., description="The name of the customer event")
    timestamp: str = Field(
        ...,
        description="The timestamp of when the customer event occurred, in ISO 8601 format",
    )
    type: EventType = Field(..., description="Event type object")


# -------------------------------------------------------

class Attribute(BaseModel):

class MailingAddress(BaseModel):

class Delivery(BaseModel):
    
class DiscountApplication(BaseModel):
    
class MoneyV2(BaseModel):
    
class CheckoutLineItem(BaseModel):

class Localization(BaseModel):

class Order(BaseModel):

class ShippingRate(BaseModel):

class Transaction(BaseModel):


class Checkout(BaseModel):
    attributes: list[Attribute] = Field(
        ...,
        description="A list of attributes accumulated throughout the checkout process.",
    )

    billingAddress: MailingAddress = Field(
        ..., description="The billing address to where the order will be charged."
    )

    # This property is only available if the shop has upgraded to Checkout Extensibility.
    buyerAcceptsMarketing: bool = Field(
        ...,
        description="Indicates whether the customer has consented to be sent marketing material via email.",
    )

    # This property is only available if the shop has upgraded to Checkout Extensibility.
    buyerAcceptsSmsMarketing: bool = Field(
        ...,
        description="Indicates whether the customer has consented to be sent marketing material via SMS.",
    )

    currencyCode: str = Field(
        ...,
        description="The three-letter code that represents the currency, for example, USD. Supported codes include standard ISO 4217 codes, legacy codes, and non- standard codes.",
    )

    delivery: Delivery = Field(
        ...,
        description="Represents the selected delivery options for a checkout. This property is only available if the shop has upgraded to Checkout Extensibility.",
    )

    discountApplications: list[DiscountApplication] = Field(
        ..., description="A list of discount applications."
    )

    # This property is only available if the shop has upgraded to Checkout Extensibility.
    discountsAmount: MoneyV2 = Field(
        ...,
        description="The total amount of the discounts applied to the price of the checkout. This property is only available if the shop has upgraded to Checkout Extensibility.",
    )

    email: str = Field(..., description="The email attached to this checkout.")

    lineItems: list[CheckoutLineItem] = Field(
        ...,
        description="A list of line item objects, each one containing information about an item in the checkout.",
    )

    # This property is only available if the shop has upgraded to Checkout Extensibility.
    localization: Localization = Field(
        ..., description="Information about the active localized experience."
    )

    order: Order = Field(..., description="The resulting order from a paid checkout.")

    phone: str = Field(
        ...,
        description="A unique phone number for the customer. Formatted using E.164 standard. For example, +16135551111.",
    )

    shippingAddress: MailingAddress = Field(
        ..., description="The shipping address to where the line items will be shipped."
    )

    shippingLine: ShippingRate = Field(
        ...,
        description="Once a shipping rate is selected by the customer it is transitioned to a shipping_line object.",
    )

    # This property is only available if the shop has upgraded to Checkout Extensibility.
    smsMarketingPhone: str = Field(
        ...,
        description="The phone number provided by the buyer after opting in to SMS marketing.",
    )

    subtotalPrice: MoneyV2 = Field(
        ..., description="The sum of the prices of all the line items in the checkout."
    )

    token: str = Field(
        ..., description="A unique identifier for a particular checkout."
    )

    totalPrice: MoneyV2 = Field(
        ...,
        description="The sum of all the prices of all the items in the checkout, including duties, taxes, and discounts.",
    )

    totalTax: MoneyV2 = Field(
        ...,
        description="The sum of all the taxes applied to the line items and shipping lines in the checkout.",
    )  # totalTax

    transactions: list[Transaction] = Field(
        ...,
        description="A list of transactions associated with a checkout or order. Certain transactions, such as credit card transactions, may only be present in the checkout_completed event.",
    )

class WebPixelsDocument(BaseModel):

class WebPixelsNavigator(BaseModel):

class WebPixelsWindow(BaseModel):


class Context(BaseModel):
    document: WebPixelsDocument = Field(
        ...,
        description="Snapshot of a subset of properties of the document object in the top frame of the browser",
    )
    navigator: WebPixelsNavigator = Field(
        ...,
        description="Snapshot of a subset of properties of the navigator object in the top frame of the browser",
    )
    window: WebPixelsWindow = Field(
        ...,
        description="Snapshot of a subset of properties of the window object in the top frame of the browser",
    )


class PixelEventsCheckoutStartedData(BaseModel):
    checkout: Checkout = Field(..., description="Checkout object")


class StandardEvent(BaseModel):
    clientId: str = Field(
        ..., description="The client-side ID of the customer, provided by Shopify"
    )
    context: Context = Field(..., description="Context object")
    data: PixelEventsCheckoutStartedData = Field(
        ..., description="Pixel Events Checkout Started Data object"
    )
    id: str = Field(..., description="The ID of the customer event")
    name: str = Field(..., description="The name of the customer event")
    timestamp: str = Field(
        ...,
        description="The timestamp of when the customer event occurred, in ISO 8601 format",
    )
    type: EventType


# alert_displayed
# cart_viewed
# checkout_address_info_submitted
# checkout_completed
# checkout_contact_info_submitted
# checkout_shipping_info_submitted
# checkout_started
# collection_viewed
# page_viewed
# payment_info_submitted
# product_added_to_cart
# product_removed_from_cart
# product_viewed
# search_submitted
# ui_extension_errored
