<!-- Generator: Widdershins v4.0.1 -->

<h1 id="cortexcommerce">CortexCommerce v1</h1>

> Scroll down for code samples, example requests and responses. Select a language for code samples from the tabs above or the mobile navigation menu.

This API allows users to:
- Browse products and categories
- Manage shopping carts and orders
- Apply discounts and process payments
- Track order history and feedback
All endpoints are secured where necessary and return JSON responses.
For authentication, use JWT tokens

Base URLs:

* <a href="http://localhost:9000/">http://localhost:9000/</a>

 License: BSD License

# Authentication

* API Key (Bearer)
    - Parameter Name: **Authorization**, in: header. JWT Authorization header using the Bearer scheme. Example: 'Bearer {token}'

<h1 id="cortexcommerce-custom-auth">Custom Auth</h1>

## api_v1_auth_activate_read

<a id="opIdapi_v1_auth_activate_read"></a>

> Code samples

`GET /api/v1/auth/activate/{uid}/{token}/`

*Activate user account*

Activate user account using the UID and token

<h3 id="api_v1_auth_activate_read-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|uid|path|string|true|none|
|token|path|string|true|none|

<h3 id="api_v1_auth_activate_read-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Account activated|None|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Invalid activation link|None|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
Bearer
</aside>

<h1 id="cortexcommerce-cart">Cart</h1>

## api_v1_carts_list

<a id="opIdapi_v1_carts_list"></a>

> Code samples

`GET /api/v1/carts/`

*Fetch cart items*

Return list of user cart items

> Example responses

> 200 Response

```json
[
  {
    "quantity": 1,
    "subtotal": "string",
    "action": "add",
    "product_id": 0,
    "created_at": "2019-08-24T14:15:22Z",
    "product": "string"
  }
]
```

<h3 id="api_v1_carts_list-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|none|Inline|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Unauthorized|None|

<h3 id="api_v1_carts_list-responseschema">Response Schema</h3>

Status Code **200**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|*anonymous*|[[Cart](#schemacart)]|false|none|none|
|» quantity|integer|false|none|none|
|» subtotal|string|false|read-only|none|
|» action|string|false|none|none|
|» product_id|integer|true|none|none|
|» created_at|string(date-time)|false|read-only|none|
|» product|string|false|read-only|none|

#### Enumerated Values

|Property|Value|
|---|---|
|action|add|
|action|remove|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
Bearer
</aside>

## api_v1_carts_create

<a id="opIdapi_v1_carts_create"></a>

> Code samples

`POST /api/v1/carts/`

*Add products to cart*

Add & remove products from cart

> Body parameter

```json
{
  "action": "add",
  "product_id": 42
}
```

<h3 id="api_v1_carts_create-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|action|body|string|false|none|
|product_id|body|integer|true|none|
|quantity|body|integer|false|none|

#### Enumerated Values

|Parameter|Value|
|---|---|
|action|add|
|action|remove|

> Example responses

> 201 Response

```json
{
  "quantity": 1,
  "subtotal": "string",
  "action": "add",
  "product_id": 0,
  "created_at": "2019-08-24T14:15:22Z",
  "product": "string"
}
```

<h3 id="api_v1_carts_create-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|none|[Cart](#schemacart)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Validation error|None|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Unauthorized|None|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
Bearer
</aside>

## api_v1_carts_cart_clear_delete

<a id="opIdapi_v1_carts_cart_clear_delete"></a>

> Code samples

`DELETE /api/v1/carts/cart/clear/`

*Clear user cart*

Remove cart items

<h3 id="api_v1_carts_cart_clear_delete-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Cart already empty|None|
|204|[No Content](https://tools.ietf.org/html/rfc7231#section-6.3.5)|Cart dropped successfully|None|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Unauthorized|None|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
Bearer
</aside>

<h1 id="cortexcommerce-order">Order</h1>

## api_v1_checkout_create

<a id="opIdapi_v1_checkout_create"></a>

> Code samples

`POST /api/v1/checkout/`

*Start checkout process*

Fetch cart information and create an invoice

> Body parameter

```json
{
  "address": "string"
}
```

<h3 id="api_v1_checkout_create-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[Checkout](#schemacheckout)|true|none|

> Example responses

> 201 Response

```json
{
  "result": "string",
  "status": "string",
  "items": [
    {
      "product": "string",
      "quantity": 0,
      "price": "string"
    }
  ],
  "skipped_items": [
    "string"
  ]
}
```

<h3 id="api_v1_checkout_create-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|Order created|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Cart empty or out of stock|None|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Unauthorized|None|

<h3 id="api_v1_checkout_create-responseschema">Response Schema</h3>

Status Code **201**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» result|string|false|none|Success message|
|» status|string|false|none|Order status|
|» items|[object]|false|none|Processed items in the order|
|»» product|string|false|none|none|
|»» quantity|integer|false|none|none|
|»» price|string|false|none|none|
|» skipped_items|[string]|false|none|Items skipped due to insufficient stock (optional)|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
Bearer
</aside>

## api_v1_checkout_invoice_list

<a id="opIdapi_v1_checkout_invoice_list"></a>

> Code samples

`GET /api/v1/checkout/invoice/`

*List order invoice*

Returns order invoice with detailed info

> Example responses

> 200 Response

```json
[
  {
    "id": 0,
    "status": "pending",
    "shipping_address": "string",
    "subtotal": "string",
    "subtotal_formatted": "string",
    "order_items": [
      {
        "id": 0,
        "quantity": 9223372036854776000,
        "price_at_purchase": "string",
        "product": "string"
      }
    ],
    "created_at": "2019-08-24T14:15:22Z"
  }
]
```

<h3 id="api_v1_checkout_invoice_list-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|none|Inline|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Unauthorized|None|

<h3 id="api_v1_checkout_invoice_list-responseschema">Response Schema</h3>

Status Code **200**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|*anonymous*|[[Order](#schemaorder)]|false|none|none|
|» id|integer|false|read-only|none|
|» status|string|false|none|none|
|» shipping_address|string|true|none|none|
|» subtotal|string|false|read-only|none|
|» subtotal_formatted|string|false|read-only|none|
|» order_items|[[OrderItem](#schemaorderitem)]|true|none|none|
|»» id|integer|false|read-only|none|
|»» quantity|integer|true|none|none|
|»» price_at_purchase|string|false|read-only|none|
|»» product|string|false|read-only|none|
|» created_at|string(date-time)|true|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|status|pending|
|status|paid|
|status|failed|
|status|shipped|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
Bearer
</aside>

<h1 id="cortexcommerce-payment">Payment</h1>

## api_v1_payments_callback_list

<a id="opIdapi_v1_payments_callback_list"></a>

> Code samples

`GET /api/v1/payments/callback/`

*Verify payment callback*

Verify payment with Zibal gateway using the given trackId

<h3 id="api_v1_payments_callback_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|trackId|query|string|true|Unique transaction ID returned from Zibal|

<h3 id="api_v1_payments_callback_list-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Payment verification success|None|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Payment failed or invalid trackId|None|
|502|[Bad Gateway](https://tools.ietf.org/html/rfc7231#section-6.6.3)|Payment gateway connection error|None|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
Bearer
</aside>

## api_v1_payments_create_create

<a id="opIdapi_v1_payments_create_create"></a>

> Code samples

`POST /api/v1/payments/create/`

*Request payment for pending order*

Return payment url and track id for pending order

<h3 id="api_v1_payments_create_create-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Payment request successfully created|None|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|No pending order or payment gateway error|None|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Unauthorized|None|
|502|[Bad Gateway](https://tools.ietf.org/html/rfc7231#section-6.6.3)|Payment gateway connection error|None|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
Bearer
</aside>

## api_v1_payments_list_list

<a id="opIdapi_v1_payments_list_list"></a>

> Code samples

`GET /api/v1/payments/list/`

*List user payment history*

Returns list of payments associated with authenticated user

> Example responses

> 200 Response

```json
[
  {
    "order": [
      {
        "id": 0,
        "status": "pending",
        "shipping_address": "string",
        "subtotal": "string",
        "subtotal_formatted": "string",
        "order_items": [
          {
            "id": 0,
            "quantity": 9223372036854776000,
            "price_at_purchase": "string",
            "product": "string"
          }
        ],
        "created_at": "2019-08-24T14:15:22Z"
      }
    ],
    "track_id": "string",
    "amount": "string",
    "formatted_amount": "string",
    "status": "pending"
  }
]
```

<h3 id="api_v1_payments_list_list-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|none|Inline|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Unauthorized|None|

<h3 id="api_v1_payments_list_list-responseschema">Response Schema</h3>

Status Code **200**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|*anonymous*|[[Payment](#schemapayment)]|false|none|none|
|» order|[[Order](#schemaorder)]|true|none|none|
|»» id|integer|false|read-only|none|
|»» status|string|false|none|none|
|»» shipping_address|string|true|none|none|
|»» subtotal|string|false|read-only|none|
|»» subtotal_formatted|string|false|read-only|none|
|»» order_items|[[OrderItem](#schemaorderitem)]|true|none|none|
|»»» id|integer|false|read-only|none|
|»»» quantity|integer|true|none|none|
|»»» price_at_purchase|string|false|read-only|none|
|»»» product|string|false|read-only|none|
|»» created_at|string(date-time)|true|none|none|
|» track_id|string¦null|false|none|none|
|» amount|string(decimal)|true|none|none|
|» formatted_amount|string|false|read-only|none|
|» status|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|status|pending|
|status|paid|
|status|failed|
|status|shipped|
|status|pending|
|status|success|
|status|failed|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
Bearer
</aside>

<h1 id="cortexcommerce-product">Product</h1>

## api_v1_products_list

<a id="opIdapi_v1_products_list"></a>

> Code samples

`GET /api/v1/products/`

*Product list*

Fetch categories by slug
Products filtering:
    - min_price
    - max_price
    - in_stock
    - brand
    - has_discount
Paginated lists of products

<h3 id="api_v1_products_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|ordering|query|string|false|Sorted by price | visit_count | created_at|
|page|query|integer|false|A page number within the paginated result set.|
|page_size|query|integer|false|Number of results to return per page.|
|q|query|string|false|Seach products|
|category|query|string|false|Category info by given slug|
|max_price|query|number|false|Filter products by max_price|
|min_price|query|number|false|Filter products by min_price|
|in_stock|query|boolean|false|Filter by stock availability|
|brand|query|string|false|Filter by brand|
|has_discount|query|boolean|false|Only show discounted products|

> Example responses

> 200 Response

```json
{
  "count": 0,
  "next": "http://example.com",
  "previous": "http://example.com",
  "results": [
    {
      "id": 0,
      "in_stock": "string",
      "stock": 9223372036854776000,
      "title": "string",
      "slug": "string",
      "brand": "string",
      "visit_count": 9223372036854776000,
      "price": 0,
      "price_formatted": "string",
      "has_discount": "string",
      "discount": "string",
      "features": "string",
      "main_image": "http://example.com",
      "avg_rating": "string",
      "created_at": "2019-08-24T14:15:22Z",
      "url": "http://example.com"
    }
  ]
}
```

<h3 id="api_v1_products_list-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|none|Inline|

<h3 id="api_v1_products_list-responseschema">Response Schema</h3>

Status Code **200**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» count|integer|true|none|none|
|» next|string(uri)¦null|false|none|none|
|» previous|string(uri)¦null|false|none|none|
|» results|[[Product](#schemaproduct)]|true|none|none|
|»» id|integer|false|read-only|none|
|»» in_stock|string|false|read-only|none|
|»» stock|integer|false|none|none|
|»» title|string|true|none|none|
|»» slug|string(slug)¦null|false|none|none|
|»» brand|string¦null|false|none|none|
|»» visit_count|integer¦null|false|none|none|
|»» price|number(decimal)|true|none|none|
|»» price_formatted|string|false|read-only|none|
|»» has_discount|string|false|read-only|none|
|»» discount|string|false|read-only|none|
|»» features|string|false|read-only|none|
|»» main_image|string(uri)¦null|false|read-only|none|
|»» avg_rating|string|false|read-only|none|
|»» created_at|string(date-time)|true|none|none|
|»» url|string(uri)|false|read-only|none|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
Bearer
</aside>

## api_v1_products_categories_list

<a id="opIdapi_v1_products_categories_list"></a>

> Code samples

`GET /api/v1/products/categories/`

*Category list*

Retrieve top-level categories along with subcategories and products

> Example responses

> 200 Response

```json
[
  {
    "title": "string",
    "breadcrumb": "string",
    "has_discount": "string",
    "discount": "string",
    "products_preview": "string",
    "subcategories": "string"
  }
]
```

<h3 id="api_v1_products_categories_list-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|none|Inline|

<h3 id="api_v1_products_categories_list-responseschema">Response Schema</h3>

Status Code **200**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|*anonymous*|[[Category](#schemacategory)]|false|none|none|
|» title|string|true|none|none|
|» breadcrumb|string|false|read-only|none|
|» has_discount|string|false|read-only|none|
|» discount|string|false|read-only|none|
|» products_preview|string|false|read-only|none|
|» subcategories|string|false|read-only|none|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
Bearer
</aside>

## api_v1_products_info_read

<a id="opIdapi_v1_products_info_read"></a>

> Code samples

`GET /api/v1/products/info/{slug}/`

*Product Detail*

Fetch product details using the slug. Visit count incremented atomically

<h3 id="api_v1_products_info_read-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|slug|path|string|true|Product slug|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "in_stock": "string",
  "stock": 9223372036854776000,
  "title": "string",
  "slug": "string",
  "brand": "string",
  "visit_count": 9223372036854776000,
  "price": 0,
  "price_formatted": "string",
  "has_discount": "string",
  "discount": "string",
  "features": "string",
  "main_image": "http://example.com",
  "avg_rating": "string",
  "created_at": "2019-08-24T14:15:22Z",
  "url": "http://example.com"
}
```

<h3 id="api_v1_products_info_read-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|none|[Product](#schemaproduct)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Transaction rolled back due to an error|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Product not found|None|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
Bearer
</aside>

<h1 id="cortexcommerce-product-likes">Product Likes</h1>

## api_v1_products_likes_list

<a id="opIdapi_v1_products_likes_list"></a>

> Code samples

`GET /api/v1/products/likes/`

*List user likes*

Retrieve list of all products liked by authenticated user

> Example responses

> 200 Response

```json
[
  {
    "product": 0,
    "associated_product": "string"
  }
]
```

<h3 id="api_v1_products_likes_list-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|List of likes|Inline|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Unauthorized|None|

<h3 id="api_v1_products_likes_list-responseschema">Response Schema</h3>

Status Code **200**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|*anonymous*|[[Like](#schemalike)]|false|none|none|
|» product|integer|true|none|none|
|» associated_product|string|false|read-only|none|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
Bearer
</aside>

## api_v1_products_likes_create

<a id="opIdapi_v1_products_likes_create"></a>

> Code samples

`POST /api/v1/products/likes/`

*Like toggler*

Toggle like/unlike for a product

> Body parameter

```json
{
  "product": 0
}
```

<h3 id="api_v1_products_likes_create-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|product|body|integer|true|ID of the product to like/unlike|

> Example responses

> 201 Response

```json
{
  "product": 0,
  "associated_product": "string"
}
```

<h3 id="api_v1_products_likes_create-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Like removed|None|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|Like created|[Like](#schemalike)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Bad request|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Product not found|None|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
Bearer
</aside>

<h1 id="cortexcommerce-feedback">Feedback</h1>

## api_v1_products_feedbacks_list

<a id="opIdapi_v1_products_feedbacks_list"></a>

> Code samples

`GET /api/v1/products/{product_id}/feedbacks/`

*List feedbacks*

List feedbacks using product_id

<h3 id="api_v1_products_feedbacks_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|ordering|query|string|false|Which field to use when ordering the results.|
|page|query|integer|false|A page number within the paginated result set.|
|page_size|query|integer|false|Number of results to return per page.|
|product_id|path|integer|true|Fetch product instance using its id|

> Example responses

> 200 Response

```json
[
  {
    "user": "string",
    "score": 1,
    "comment": "string",
    "product_id": 0,
    "created_at": "2019-08-24T14:15:22Z",
    "product": "string"
  }
]
```

<h3 id="api_v1_products_feedbacks_list-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|none|Inline|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Unauthorized|None|

<h3 id="api_v1_products_feedbacks_list-responseschema">Response Schema</h3>

Status Code **200**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|*anonymous*|[[Feedback](#schemafeedback)]|false|none|none|
|» user|string|false|read-only|none|
|» score|integer|true|none|Rating from 1 to 5 stars|
|» comment|string|true|none|none|
|» product_id|integer|false|none|none|
|» created_at|string(date-time)|false|read-only|none|
|» product|string|false|read-only|none|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
Bearer
</aside>

## api_v1_products_feedbacks_create

<a id="opIdapi_v1_products_feedbacks_create"></a>

> Code samples

`POST /api/v1/products/{product_id}/feedbacks/`

*Create Feedback*

Submit feedback for a product using its ID.

> Body parameter

```json
{
  "score": 1,
  "comment": "string",
  "product_id": 0
}
```

<h3 id="api_v1_products_feedbacks_create-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[Feedback](#schemafeedback)|true|none|
|product_id|path|string|true|none|

> Example responses

> 201 Response

```json
{
  "user": "string",
  "score": 1,
  "comment": "string",
  "product_id": 0,
  "created_at": "2019-08-24T14:15:22Z",
  "product": "string"
}
```

<h3 id="api_v1_products_feedbacks_create-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|none|[Feedback](#schemafeedback)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Bad request|None|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Unauthorized|None|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
Bearer
</aside>

<h1 id="cortexcommerce-auth">auth</h1>

## auth_jwt_create_create

<a id="opIdauth_jwt_create_create"></a>

> Code samples

`POST /auth/jwt/create/`

Takes a set of user credentials and returns an access and refresh JSON web
token pair to prove the authentication of those credentials.

> Body parameter

```json
{
  "email": "string",
  "password": "string"
}
```

<h3 id="auth_jwt_create_create-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[TokenObtainPair](#schematokenobtainpair)|true|none|

> Example responses

> 201 Response

```json
{
  "email": "string",
  "password": "string"
}
```

<h3 id="auth_jwt_create_create-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|none|[TokenObtainPair](#schematokenobtainpair)|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
Bearer
</aside>

## auth_jwt_logout_create

<a id="opIdauth_jwt_logout_create"></a>

> Code samples

`POST /auth/jwt/logout/`

Takes a token and blacklists it. Must be used with the
`rest_framework_simplejwt.token_blacklist` app installed.

> Body parameter

```json
{
  "refresh": "string"
}
```

<h3 id="auth_jwt_logout_create-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[TokenBlacklist](#schematokenblacklist)|true|none|

> Example responses

> 201 Response

```json
{
  "refresh": "string"
}
```

<h3 id="auth_jwt_logout_create-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|none|[TokenBlacklist](#schematokenblacklist)|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
Bearer
</aside>

## auth_jwt_verify_create

<a id="opIdauth_jwt_verify_create"></a>

> Code samples

`POST /auth/jwt/verify/`

Takes a token and indicates if it is valid.  This view provides no
information about a token's fitness for a particular use.

> Body parameter

```json
{
  "token": "string"
}
```

<h3 id="auth_jwt_verify_create-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[TokenVerify](#schematokenverify)|true|none|

> Example responses

> 201 Response

```json
{
  "token": "string"
}
```

<h3 id="auth_jwt_verify_create-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|none|[TokenVerify](#schematokenverify)|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
Bearer
</aside>

## auth_users_create

<a id="opIdauth_users_create"></a>

> Code samples

`POST /auth/users/`

> Body parameter

```json
{
  "email": "user@example.com",
  "username": "string",
  "password": "string"
}
```

<h3 id="auth_users_create-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[CustomUserCreate](#schemacustomusercreate)|true|none|

> Example responses

> 201 Response

```json
{
  "email": "user@example.com",
  "username": "string",
  "password": "string"
}
```

<h3 id="auth_users_create-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|none|[CustomUserCreate](#schemacustomusercreate)|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
Bearer
</aside>

## auth_users_reset_password

<a id="opIdauth_users_reset_password"></a>

> Code samples

`POST /auth/users/reset_password/`

> Body parameter

```json
{
  "email": "user@example.com"
}
```

<h3 id="auth_users_reset_password-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[SendEmailReset](#schemasendemailreset)|true|none|

> Example responses

> 201 Response

```json
{
  "email": "user@example.com"
}
```

<h3 id="auth_users_reset_password-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|none|[SendEmailReset](#schemasendemailreset)|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
Bearer
</aside>

## auth_users_reset_password_confirm

<a id="opIdauth_users_reset_password_confirm"></a>

> Code samples

`POST /auth/users/reset_password_confirm/`

> Body parameter

```json
{
  "uid": "string",
  "token": "string",
  "new_password": "string"
}
```

<h3 id="auth_users_reset_password_confirm-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[PasswordResetConfirm](#schemapasswordresetconfirm)|true|none|

> Example responses

> 201 Response

```json
{
  "uid": "string",
  "token": "string",
  "new_password": "string"
}
```

<h3 id="auth_users_reset_password_confirm-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|none|[PasswordResetConfirm](#schemapasswordresetconfirm)|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
Bearer
</aside>

# Schemas

<h2 id="tocS_Cart">Cart</h2>
<!-- backwards compatibility -->
<a id="schemacart"></a>
<a id="schema_Cart"></a>
<a id="tocScart"></a>
<a id="tocscart"></a>

```json
{
  "quantity": 1,
  "subtotal": "string",
  "action": "add",
  "product_id": 0,
  "created_at": "2019-08-24T14:15:22Z",
  "product": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|quantity|integer|false|none|none|
|subtotal|string|false|read-only|none|
|action|string|false|none|none|
|product_id|integer|true|none|none|
|created_at|string(date-time)|false|read-only|none|
|product|string|false|read-only|none|

#### Enumerated Values

|Property|Value|
|---|---|
|action|add|
|action|remove|

<h2 id="tocS_Checkout">Checkout</h2>
<!-- backwards compatibility -->
<a id="schemacheckout"></a>
<a id="schema_Checkout"></a>
<a id="tocScheckout"></a>
<a id="tocscheckout"></a>

```json
{
  "address": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|address|string|true|none|Delivery address|

<h2 id="tocS_OrderItem">OrderItem</h2>
<!-- backwards compatibility -->
<a id="schemaorderitem"></a>
<a id="schema_OrderItem"></a>
<a id="tocSorderitem"></a>
<a id="tocsorderitem"></a>

```json
{
  "id": 0,
  "quantity": 9223372036854776000,
  "price_at_purchase": "string",
  "product": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|id|integer|false|read-only|none|
|quantity|integer|true|none|none|
|price_at_purchase|string|false|read-only|none|
|product|string|false|read-only|none|

<h2 id="tocS_Order">Order</h2>
<!-- backwards compatibility -->
<a id="schemaorder"></a>
<a id="schema_Order"></a>
<a id="tocSorder"></a>
<a id="tocsorder"></a>

```json
{
  "id": 0,
  "status": "pending",
  "shipping_address": "string",
  "subtotal": "string",
  "subtotal_formatted": "string",
  "order_items": [
    {
      "id": 0,
      "quantity": 9223372036854776000,
      "price_at_purchase": "string",
      "product": "string"
    }
  ],
  "created_at": "2019-08-24T14:15:22Z"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|id|integer|false|read-only|none|
|status|string|false|none|none|
|shipping_address|string|true|none|none|
|subtotal|string|false|read-only|none|
|subtotal_formatted|string|false|read-only|none|
|order_items|[[OrderItem](#schemaorderitem)]|true|none|none|
|created_at|string(date-time)|true|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|status|pending|
|status|paid|
|status|failed|
|status|shipped|

<h2 id="tocS_Payment">Payment</h2>
<!-- backwards compatibility -->
<a id="schemapayment"></a>
<a id="schema_Payment"></a>
<a id="tocSpayment"></a>
<a id="tocspayment"></a>

```json
{
  "order": [
    {
      "id": 0,
      "status": "pending",
      "shipping_address": "string",
      "subtotal": "string",
      "subtotal_formatted": "string",
      "order_items": [
        {
          "id": 0,
          "quantity": 9223372036854776000,
          "price_at_purchase": "string",
          "product": "string"
        }
      ],
      "created_at": "2019-08-24T14:15:22Z"
    }
  ],
  "track_id": "string",
  "amount": "string",
  "formatted_amount": "string",
  "status": "pending"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|order|[[Order](#schemaorder)]|true|none|none|
|track_id|string¦null|false|none|none|
|amount|string(decimal)|true|none|none|
|formatted_amount|string|false|read-only|none|
|status|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|status|pending|
|status|success|
|status|failed|

<h2 id="tocS_Product">Product</h2>
<!-- backwards compatibility -->
<a id="schemaproduct"></a>
<a id="schema_Product"></a>
<a id="tocSproduct"></a>
<a id="tocsproduct"></a>

```json
{
  "id": 0,
  "in_stock": "string",
  "stock": 9223372036854776000,
  "title": "string",
  "slug": "string",
  "brand": "string",
  "visit_count": 9223372036854776000,
  "price": 0,
  "price_formatted": "string",
  "has_discount": "string",
  "discount": "string",
  "features": "string",
  "main_image": "http://example.com",
  "avg_rating": "string",
  "created_at": "2019-08-24T14:15:22Z",
  "url": "http://example.com"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|id|integer|false|read-only|none|
|in_stock|string|false|read-only|none|
|stock|integer|false|none|none|
|title|string|true|none|none|
|slug|string(slug)¦null|false|none|none|
|brand|string¦null|false|none|none|
|visit_count|integer¦null|false|none|none|
|price|number(decimal)|true|none|none|
|price_formatted|string|false|read-only|none|
|has_discount|string|false|read-only|none|
|discount|string|false|read-only|none|
|features|string|false|read-only|none|
|main_image|string(uri)¦null|false|read-only|none|
|avg_rating|string|false|read-only|none|
|created_at|string(date-time)|true|none|none|
|url|string(uri)|false|read-only|none|

<h2 id="tocS_Category">Category</h2>
<!-- backwards compatibility -->
<a id="schemacategory"></a>
<a id="schema_Category"></a>
<a id="tocScategory"></a>
<a id="tocscategory"></a>

```json
{
  "title": "string",
  "breadcrumb": "string",
  "has_discount": "string",
  "discount": "string",
  "products_preview": "string",
  "subcategories": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|title|string|true|none|none|
|breadcrumb|string|false|read-only|none|
|has_discount|string|false|read-only|none|
|discount|string|false|read-only|none|
|products_preview|string|false|read-only|none|
|subcategories|string|false|read-only|none|

<h2 id="tocS_Like">Like</h2>
<!-- backwards compatibility -->
<a id="schemalike"></a>
<a id="schema_Like"></a>
<a id="tocSlike"></a>
<a id="tocslike"></a>

```json
{
  "product": 0,
  "associated_product": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|product|integer|true|none|none|
|associated_product|string|false|read-only|none|

<h2 id="tocS_Feedback">Feedback</h2>
<!-- backwards compatibility -->
<a id="schemafeedback"></a>
<a id="schema_Feedback"></a>
<a id="tocSfeedback"></a>
<a id="tocsfeedback"></a>

```json
{
  "user": "string",
  "score": 1,
  "comment": "string",
  "product_id": 0,
  "created_at": "2019-08-24T14:15:22Z",
  "product": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|user|string|false|read-only|none|
|score|integer|true|none|Rating from 1 to 5 stars|
|comment|string|true|none|none|
|product_id|integer|false|none|none|
|created_at|string(date-time)|false|read-only|none|
|product|string|false|read-only|none|

<h2 id="tocS_TokenObtainPair">TokenObtainPair</h2>
<!-- backwards compatibility -->
<a id="schematokenobtainpair"></a>
<a id="schema_TokenObtainPair"></a>
<a id="tocStokenobtainpair"></a>
<a id="tocstokenobtainpair"></a>

```json
{
  "email": "string",
  "password": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|email|string|true|none|none|
|password|string|true|none|none|

<h2 id="tocS_TokenBlacklist">TokenBlacklist</h2>
<!-- backwards compatibility -->
<a id="schematokenblacklist"></a>
<a id="schema_TokenBlacklist"></a>
<a id="tocStokenblacklist"></a>
<a id="tocstokenblacklist"></a>

```json
{
  "refresh": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|refresh|string|true|none|none|

<h2 id="tocS_TokenVerify">TokenVerify</h2>
<!-- backwards compatibility -->
<a id="schematokenverify"></a>
<a id="schema_TokenVerify"></a>
<a id="tocStokenverify"></a>
<a id="tocstokenverify"></a>

```json
{
  "token": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|token|string|true|none|none|

<h2 id="tocS_CustomUserCreate">CustomUserCreate</h2>
<!-- backwards compatibility -->
<a id="schemacustomusercreate"></a>
<a id="schema_CustomUserCreate"></a>
<a id="tocScustomusercreate"></a>
<a id="tocscustomusercreate"></a>

```json
{
  "email": "user@example.com",
  "username": "string",
  "password": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|email|string(email)|true|none|none|
|username|string|false|none|none|
|password|string|true|none|none|

<h2 id="tocS_SendEmailReset">SendEmailReset</h2>
<!-- backwards compatibility -->
<a id="schemasendemailreset"></a>
<a id="schema_SendEmailReset"></a>
<a id="tocSsendemailreset"></a>
<a id="tocssendemailreset"></a>

```json
{
  "email": "user@example.com"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|email|string(email)|true|none|none|

<h2 id="tocS_PasswordResetConfirm">PasswordResetConfirm</h2>
<!-- backwards compatibility -->
<a id="schemapasswordresetconfirm"></a>
<a id="schema_PasswordResetConfirm"></a>
<a id="tocSpasswordresetconfirm"></a>
<a id="tocspasswordresetconfirm"></a>

```json
{
  "uid": "string",
  "token": "string",
  "new_password": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|uid|string|true|none|none|
|token|string|true|none|none|
|new_password|string|true|none|none|

