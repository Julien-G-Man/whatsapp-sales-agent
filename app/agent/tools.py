# Tool schema definitions passed to the Claude API.
# These describe WHAT tools exist; the implementations live in app/tools/.

TOOL_QUERY_INVENTORY = {
    "name": "query_inventory",
    "description": "Check stock level and price for a product. Use when a customer asks about availability or price.",
    "input_schema": {
        "type": "object",
        "properties": {
            "product_name": {
                "type": "string",
                "description": "Product name or partial name to search (e.g. 'mafuta', 'huile 5L')",
            }
        },
        "required": ["product_name"],
    },
}

TOOL_INITIATE_MOMO_PAYMENT = {
    "name": "initiate_momo_payment",
    "description": (
        "Initiate an MTN MoMo payment request. Call this after the customer confirms their order. "
        "Sends a push request to the customer's phone. The customer must approve it."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "description": "List of ordered items",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "qty": {"type": "integer"},
                        "price_xaf": {"type": "integer"},
                    },
                    "required": ["name", "qty", "price_xaf"],
                },
            },
            "total_xaf": {
                "type": "integer",
                "description": "Total amount in XAF (CFA francs)",
            },
        },
        "required": ["items", "total_xaf"],
    },
}

TOOL_CHECK_ORDER_STATUS = {
    "name": "check_order_status",
    "description": "Check the status of an existing order by its ID.",
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {
                "type": "integer",
                "description": "The order ID to look up",
            }
        },
        "required": ["order_id"],
    },
}

TOOL_GET_BUSINESS_HOURS = {
    "name": "get_business_hours",
    "description": "Get the business opening hours and contact details.",
    "input_schema": {"type": "object", "properties": {}, "required": []},
}

TOOL_GET_REVENUE_SUMMARY = {
    "name": "get_revenue_summary",
    "description": "Get revenue totals and order count for a time period.",
    "input_schema": {
        "type": "object",
        "properties": {
            "period": {
                "type": "string",
                "enum": ["today", "yesterday", "week", "month"],
                "description": "Time period for the summary",
            }
        },
        "required": ["period"],
    },
}

TOOL_GET_TOP_PRODUCTS = {
    "name": "get_top_products",
    "description": "Get the best-selling products for a given time period.",
    "input_schema": {
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "description": "Number of top products to return (default 3)"},
            "period": {
                "type": "string",
                "enum": ["today", "yesterday", "week", "month"],
            },
        },
        "required": ["period"],
    },
}

TOOL_LIST_PENDING_ORDERS = {
    "name": "list_pending_orders",
    "description": "List all orders that are pending payment or fulfilment.",
    "input_schema": {"type": "object", "properties": {}, "required": []},
}

TOOL_UPDATE_INVENTORY = {
    "name": "update_inventory",
    "description": "Update the stock quantity of a product.",
    "input_schema": {
        "type": "object",
        "properties": {
            "product_name": {"type": "string", "description": "Product name to update"},
            "new_qty": {"type": "integer", "description": "New stock quantity"},
        },
        "required": ["product_name", "new_qty"],
    },
}

TOOL_GET_FAILED_PAYMENTS = {
    "name": "get_failed_payments",
    "description": "Get a list of recent failed MoMo payment transactions.",
    "input_schema": {
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "description": "Max number of results (default 10)"}
        },
        "required": [],
    },
}

TOOL_GET_CUSTOMER_HISTORY = {
    "name": "get_customer_history",
    "description": "Get the order history for a specific customer phone number.",
    "input_schema": {
        "type": "object",
        "properties": {
            "customer_phone": {
                "type": "string",
                "description": "Customer phone number in international format",
            }
        },
        "required": ["customer_phone"],
    },
}

TOOL_SEND_BROADCAST = {
    "name": "send_broadcast",
    "description": "Send a WhatsApp message to a list of phone numbers.",
    "input_schema": {
        "type": "object",
        "properties": {
            "message": {"type": "string", "description": "Message to broadcast"},
            "phones": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of phone numbers to send to",
            },
        },
        "required": ["message", "phones"],
    },
}
