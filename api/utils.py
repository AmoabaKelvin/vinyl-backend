from typing import Union


def return_structured_data(status: str, results: Union[str, dict], details: str):
    """
    Returned a structured data which will be used to send all response
    Args:
        status: success or failure
        results: a dictionary of results
        details: a string of details
    Returns:
        A dictionary of structured data
    >>> return_structured_data('success', {'result': 'result'}, 'details')
    {'status': 'success', 'result': {'result': 'result'}, 'details': 'details'}

    >>> return_structured_data('failure', 'result', 'details')
    {'status': 'failure', 'result': 'result', 'details': 'details'}
    """
    return {
        'status': status,
        'result': results,
        'details': details,
    }
