# this will hold functions that interact with the stripe api
from typing import Tuple

import stripe


def retrieve_connect_account_balance(account_id: str) -> Tuple[str, str]:
    """
    Retrieve account balance for a user(artist).
    """
    # https://stripe.com/docs/api/balance/balance_object
    response: dict = stripe.Balance.retrieve(stripe_account=account_id)
    available_balance = response['available'][0]['amount']
    pending_balance = response['pending'][0]['amount']
    return available_balance, pending_balance


def retrieve_bank_account_info(account_id: str) -> str:
    """
    Retrieve bank account information for a user(artist).
    """
    # https://stripe.com/docs/api/external_account_bank_accounts/retrieve
    response: dict = stripe.Account.retrieve(account_id)
    bank_id: str = response['external_accounts']['data'][0]['id']
    return bank_id


def initiate_payout_request(user_account: str, amount: int, currency: str = 'usd'):
    """
    Initiate a payout request for a user(artist).
    """
    # https://stripe.com/docs/api/payouts/create
    response: dict = stripe.Payout.create(
        amount=int(amount / 10),
        currency=currency,
        stripe_account=user_account,
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


def update_account_information(account_id: str, update_data: dict) -> dict:
    """
    Update account information for a user(artist).
    """
    # https://stripe.com/docs/api/accounts/update
    response: dict = stripe.Account.modify(
        account_id,
        business_type='individual',
        metadata=update_data,
    )
    return response


def create_payment_intent(
    title: str, artist: str, song_id, amount, destination: str, customer: str
):
    """
    Create a payment intent and return the client secret
    Args:
        title: The title of the song being bought.
        artist: The username of the artist to which that song belongs.
        amount: amount to be paid
        destination: stripe account id of the recipient
        customer: stripe account id of the customer
    Returns:
        client_secret: client secret of the payment intent
    https://stripe.com/docs/api/payment_intents/create
    """
    # The price of the song needs to be an instance of an interger
    # or else stripe will throw an error.
    # INFO: 100 units is 1 dollar in stripe.
    price: int = int(amount * 100)
    response: dict = stripe.PaymentIntent.create(
        amount=price,
        currency='usd',
        application_fee_amount=int(price * 0.03),
        transfer_data={
            'destination': destination,
        },
        automatic_payment_methods={'enabled': True},
        customer=customer,
        description=f"Payment for song: {title} by {artist}",
        metadata={'song_id': song_id},
    )
    return response


def retrieve_account_information(account_id: str) -> dict:
    """
    Retrieve account information for a user.
    Args:
        account_id: stripe account id of the user
    Returns:
        response: dictionary of account information
    https://stripe.com/docs/api/accounts/retrieve
    """
    response: dict = stripe.Account.retrieve(account_id)
    return response


def list_artist_transactions(account_id: str) -> dict:
    """
    List all balance transactions for an artist.
    Args:
        account_id: stripe account id of the artist
    Returns:
        response: dictionary of balance transactions
    https://stripe.com/docs/api/customer_balance_transactions/list
    """
    response: dict = stripe.Transfer.list(stripe_account=account_id)
    return response


def list_transactions_for_a_customer(account_id: str):
    """
    List all transactions for a user.
    Args:
        account_id: stripe account id of the user
    Returns:
        response: dictionary of transactions
    https://stripe.com/docs/api/customer_balance_transactions/list
    """
    response: dict = stripe.Customer.list_balance_transactions(account_id)
    return response


def fetch_payment_intents(customer_id: str) -> dict:
    """
    Fetch the payment intents for a customer.
    Args:
        customer_id: the customer id of the user to fetch payment intents for.
    Returns:
        payment_intents dict
    """
    response: dict = stripe.PaymentIntent.list(customer=customer_id)
    return response


def request_refund(customer_id: str, song_id: int) -> dict:
    """
    Request af refund on a payment intent.
    Args:
        customer_id: The customer_id of the user requesting refund.
        song_id: The song id of the song to request refund on.
    Returns:
        The status of the refund
    https://stripe.com/docs/api/refunds/create
    """
    response = fetch_payment_intents(customer_id)
    payment_intents: list = response['data']
    payment_intent_to_refund: int = None
    for index, value in enumerate(payment_intents):
        if value['metadata']['song_id'] == str(song_id):
            payment_intent_to_refund = index
    # the index of the actual payment intent to refund to has been obtained.
    # proceed to retrieve the payment intent id
    payment_intent_id = payment_intents[payment_intent_to_refund]['id']
    refund: dict = stripe.Refund.create(payment_intent=payment_intent_id)
    return refund
