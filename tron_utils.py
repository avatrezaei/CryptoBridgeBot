from tronpy import Tron
from tronpy import Address
from tronpy.keys import PrivateKey
import os 
from database import save_user_address, get_user_address, update_user_balance
 


# Set up the Tron connection
TRON_PRIVATE_KEY = os.environ.get("TRON_PRIVATE_KEY")
tron = Tron(network='mainnet') 

USDT_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"  # TRC20 USDT contract address
BUSD_CONTRACT = "TA6vEwBMZCwFZf1eMddACNWfho1rACxL3X"  # TRC20 BUSD contract address

def deposit_address(user_id: int) -> str:
    # Check if the user already has an address in the database
    existing_address = get_user_address(user_id)
    if existing_address:
        return existing_address

    # Generate a unique deposit address for the user
    private_key = PrivateKey.random()
    public_key = private_key.public_key
    tron_address = Address.from_public_key(public_key)
    # Save user_id <-> address mapping in your database
    save_user_address(user_id, tron_address.base58) 
    return tron_address.base58 

def process_withdrawal(user_id: int, amount: float, currency: str) -> bool:
    # Check the user's balance
    user_address = get_user_address(user_id)
    if not user_address:
        return False

    token_contract = USDT_CONTRACT if currency == "USDT" else BUSD_CONTRACT
    user_balance = get_trc20_token_balance(user_address, token_contract)

    # If sufficient balance, initiate a withdrawal transaction
    if user_balance >= amount:
        # Assume the withdrawal is sent to a predetermined address
        withdrawal_address = "your_destination_tron_address"

        # Send the withdrawal amount
        send_trc20_token(withdrawal_address, amount, token_contract)

        # Update the user's balance in your database
        new_balance = user_balance - amount
        update_user_balance(user_id, currency.lower(), new_balance)

        return True
    else:
        return False


from database import get_user_balances

def get_balances(user_id: int) -> dict:
    # Query user's balances (USDT and BUSD) from your database
    balances = get_user_balances(user_id)
    
    # If user not found in the database, return balances as 0
    if not balances:
        return {'usdt': 0, 'busd': 0}
    
    return balances


# Additional helper functions for interacting with the Tron network
def send_trc20_token(to_address: str, amount: int, token_contract: str) -> str:
    """Send TRC20 tokens to a given address."""
    txn = (
        tron.transaction_builder.trigger_smart_contract(
            wallet.address,
            token_contract,
            "transfer(address,uint256)",
            [
                {"type": "address", "value": to_address},
                {"type": "uint256", "value": int(amount * 1e6)},
            ],
            fee_limit=1_000_000,
            call_value=0,
        )
        .build()
        .sign(wallet.private_key)
        .inspect()
        .broadcast()
    )

    return txn["txID"]

def get_trc20_token_balance(user_address: str, token_contract: str) -> float:
    """Get the TRC20 token balance of a given address."""
    contract_result = tron.trx.get_function_call_result(
        token_contract,
        "balanceOf(address)",
        [{"type": "address", "value": user_address}],
    )

    balance = int(contract_result["constant_result"][0], 16) / 1e6
    return balance
