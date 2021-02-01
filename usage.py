import os

from newton_wrapper import Newton

from dotenv import load_dotenv
load_dotenv()

newton = Newton(os.getenv("NEWTON_API_CLIENT_ID"),
                os.getenv("NEWTON_API_SECRET_KEY"))

# Client id and secret key is optional in the constructor and can be set after with the set_client_id(CLIENT_ID) and set_secret_key(SECRET_KEY) methods
# newton.set_client_id(os.getenv("NEWTON_API_CLIENT_ID"))
# newton.set_secret_key(os.getenv("NEWTON_API_SECRET_KEY"))

# PUBLIC

# Get the maker and taker fees that will be applied to your order.
print("Fees:", newton.get_fees())

# To get the health status of the Newton API.
print("Server status:", newton.healthcheck())

# Get the maximum amount possible to create an order per asset.
print("Maximum trade amounts:", newton.get_max_trade())

# Get the minimum amount needed to create an order per asset.
print("Minimum trade amounts:", newton.get_min_trade())

# Receive the list of supported symbols.
print("Symbols:", newton.get_symbols())

# Get the tick size for the different symbols.
print("Symbols tick sizes:", newton.get_tick_sizes())


# PRIVATE

# Get the history of actions you made.
print("Account actions:", newton.get_actions())

# Get the balances of every asset.
print("Account balances:", newton.get_balances())

# Get the history of all your orders.
print("Account order history:", newton.get_order_history())

# Get the list of all your open orders.
print("Account open orders:", newton.get_open_orders())
