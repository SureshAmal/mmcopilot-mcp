from dotenv import load_dotenv

load_dotenv()
import mm_strategy_create
from mm_strategy_create.models.response_dto import ResponseDto
from mm_strategy_create.models.scalping_dto import ScalpingDto
from mm_strategy_create.rest import ApiException
import os
from pprint import pprint

# Defining the host is optional and defaults to https://api.marketmaya.com/api
# See configuration.py for a list of all supported configuration parameters.
configuration = mm_strategy_create.Configuration(host="https://api.marketmaya.com/api")

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = mm_strategy_create.Configuration(
    access_token=os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with mm_strategy_create.ApiClient(configuration) as api_client:
    json = {
        "id": "",
        "strategy_name": "SILVER Scalping 123244",
        "short_description": "Buy SILVER Fut at every 200 points down side and book profit at 200 points.",
        "long_description": "Buy SILVER Fut at every 200 points down side and book profit at 200 points.",
        "strategy_id": "YioJhK5IqBULe8fPLMnXaAaC0$aC0$",
        "mix_name": "SILVER FUT NEAR MONTHLY",
        "main_exchange": "MCX",
        "main_segment": "FUT",
        "main_symbol": "SILVER",
        "main_contract": "NEAR",
        "main_expiry": "MONTHLY",
        "product_type": "NRML",
        "exit_order_product_type": "",
        "qty_type": "Qty",
        "qty": 1,
        "lot": 1,
        "atm": 0,
        "strike_price": 0,
        "option_type": "",
        "intraday_entry_time": "9:5",
        "intraday_exit_time": "23:50",
        "is_intraday": "false",
        "jobbing_side": "BUY",
        "jobbing_start_price": 0,
        "jobbing_end_price": 0,
        "average_by": "Point",
        "average_value": 200,
        "target_by": "Point",
        "target": 0,
        "intraday_target": 200,
        "maximum_steps": 50,
        "maximum_target_steps": 0,
        "sqroff_on_maximum_steps": "false",
        "calculate_qty_on_market_jump": "false",
        "allow_update_parameters": "true",
        "order_type": "Market Order",
        "no_of_limit_order_retry": 0,
        "retry_at_every_seconds": 0,
        "market_order_after_retry": "false",
        "reset_cycle_by_master_tpsl": "true",
        "rollover_before_days": 5,
        "is_auto_rollover": "true",
        "is_add_hedge_leg": "false",
        "rollover_time": "22:45",
        "master_tp_money": 0,
        "master_sl_money": 0,
        "reset_cycle_on_positive_mtm": 0,
        "required_margin": 100000,
        "is_trail_sl": "false",
        "profit_move": 0,
        "sl_move": 0,
        "no_of_trail_sl": 0,
        "scalping_opening_qty": 0,
        "increase_qty_on_avg": "false",
        "increase_qty": 0,
        "increase_qty_type": "null",
        "rebacktest": "false",
        "sub": [],
        "effect_all_sub_strategies": "false",
    }
    # Create an instance of the API class
    api_instance = mm_strategy_create.MainStrategyApi(api_client)
    scalping_dto = mm_strategy_create.ScalpingDto().from_json(json)  # ScalpingDto |

    try:
        # Create Scalping Strategy
        api_response = api_instance.create_scalping_strategy(scalping_dto)
        print("The response of MainStrategyApi->create_scalping_strategy:\n")
        pprint(api_response)
    except Exception as e:
        print(
            "Exception when calling MainStrategyApi->create_scalping_strategy: %s\n" % e
        )
