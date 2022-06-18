# this will hold functions that interact with the stripe api
from typing import Tuple

import stripe
from api.utils import return_structured_data
from rest_framework.response import Response


def retrive_connect_account_balance(account_id: str) -> Tuple[str, str]:
    """
    Retrieve account balance for a user(artist).
    """
    # https://stripe.com/docs/api/balance/balance_object
    response: dict = stripe.Balance.retrieve(stripe_account='acct_1LByrHQjPLYfvCoi')
    available_balance = response['available'][0]['amount']
    pending_balance = response['pending'][0]['amount']
    print(available_balance, pending_balance)
    return available_balance, pending_balance


def retrive_bank_account_info(account_id: str) -> str:
    """
    Retrieve bank account information for a user(artist).
    """
    # https://stripe.com/docs/api/external_account_bank_accounts/retrieve

    # for testing 'acct_1LByrHQjPLYfvCoi'
    response: dict = stripe.Account.retrieve('acct_1LByrHQjPLYfvCoi')
    bank_id: str = response['external_accounts']['data'][0]['id']
    return bank_id


def initiate_payout_request(bank_id: str, amount: int, currency: str = 'usd') -> dict:
    """
    Initiate a payout request for a user(artist).
    """
    # https://stripe.com/docs/api/payouts/create
    response: dict = stripe.Payout.create(
        amount=amount,
        currency=currency,
        destination=bank_id,
    )
    return response


def create_ephemeral_key(customer_id: str) -> str:
    """
    Create an ephemeral key for a user(artist).
    """
    # https://stripe.com/docs/api/tokens/create_ephemeral
    response: dict = stripe.EphemeralKey.create(
        customer=customer_id, stripe_version='2020-08-27'
    )
    return response.secret
