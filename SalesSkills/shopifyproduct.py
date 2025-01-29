# The response format can be changed based on the event
# Might create a mapper that transforms this response to a better format that the llm find easier to understand

{
    "data": {
        "products": {
            "edges": [
                {
                    "node": {
                        "id": "gid://shopify/Product/8405942468806",
                        "title": "Gift Card",
                        "description": "This is a gift card for the store",
                        "handle": "gift-card",
                        "priceRangeV2": {
                            "minVariantPrice": {
                                "amount": "10.0",
                                "currencyCode": "AED",
                            },
                            "maxVariantPrice": {
                                "amount": "100.0",
                                "currencyCode": "AED",
                            },
                        },
                        "images": {
                            "edges": [
                                {
                                    "node": {
                                        "originalSrc": "https://cdn.shopify.com/s/files/1/0659/8921/4406/files/gift_card.png?v=1734964878",
                                        "altText": "Gift card that shows text: Generated data gift card",
                                    }
                                }
                            ]
                        },
                        "variants": {
                            "edges": [
                                {
                                    "node": {
                                        "id": "gid://shopify/ProductVariant/44318296834246",
                                        "title": "$10",
                                        "price": "10.00",
                                        "sku": null,
                                        "inventoryQuantity": 0,
                                    }
                                },
                                {
                                    "node": {
                                        "id": "gid://shopify/ProductVariant/44318296867014",
                                        "title": "$25",
                                        "price": "25.00",
                                        "sku": null,
                                        "inventoryQuantity": 0,
                                    }
                                },
                                {
                                    "node": {
                                        "id": "gid://shopify/ProductVariant/44318296899782",
                                        "title": "$50",
                                        "price": "50.00",
                                        "sku": null,
                                        "inventoryQuantity": 0,
                                    }
                                },
                                {
                                    "node": {
                                        "id": "gid://shopify/ProductVariant/44318296932550",
                                        "title": "$100",
                                        "price": "100.00",
                                        "sku": null,
                                        "inventoryQuantity": 0,
                                    }
                                },
                            ]
                        },
                        "status": "ACTIVE",
                        "createdAt": "2024-12-23T14:41:16Z",
                        "updatedAt": "2024-12-24T02:41:27Z",
                    }
                },
                {
                    "node": {
                        "id": "gid://shopify/Product/8405942501574",
                        "title": "The Inventory Not Tracked Snowboard",
                        "description": "",
                        "handle": "the-inventory-not-tracked-snowboard",
                        "priceRangeV2": {
                            "minVariantPrice": {
                                "amount": "949.95",
                                "currencyCode": "AED",
                            },
                            "maxVariantPrice": {
                                "amount": "949.95",
                                "currencyCode": "AED",
                            },
                        },
                        "images": {
                            "edges": [
                                {
                                    "node": {
                                        "originalSrc": "https://cdn.shopify.com/s/files/1/0659/8921/4406/files/snowboard_purple_hydrogen.png?v=1734964878",
                                        "altText": "Top and bottom view of a snowboard. The top view shows a centred hexagonal logo for Hydrogen that\n          appears to radiate outwards, as well as some overlapping hexagons at the bottom. The bottom view shows an\n          abstract angular grid in purples.",
                                    }
                                }
                            ]
                        },
                        "variants": {
                            "edges": [
                                {
                                    "node": {
                                        "id": "gid://shopify/ProductVariant/44318296998086",
                                        "title": "Default Title",
                                        "price": "949.95",
                                        "sku": "sku-untracked-1",
                                        "inventoryQuantity": 0,
                                    }
                                }
                            ]
                        },
                        "status": "ACTIVE",
                        "createdAt": "2024-12-23T14:41:16Z",
                        "updatedAt": "2024-12-24T02:41:45Z",
                    }
                },
            ],
            "pageInfo": {
                "hasNextPage": true,
                "endCursor": "eyJsYXN0X2lkIjo4NDA1OTQyNTAxNTc0LCJsYXN0X3ZhbHVlIjoiODQwNTk0MjUwMTU3NCJ9",
            },
        }
    },
    "extensions": {
        "cost": {
            "requestedQueryCost": 12,
            "actualQueryCost": 11,
            "throttleStatus": {
                "maximumAvailable": 2000,
                "currentlyAvailable": 1989,
                "restoreRate": 100,
            },
        }
    },
}
