Requirements:
    1) python 3.7 or greater version
        If not installed, go to https://www.python.org/downloads/ to download it and install it.
    2) pip
        If not installed, go to https://pip.pypa.io/en/stable/installation/ and follow the instructions.
    3) Once python and pip are installed, run
        $ pip install -U pytest

Usage:
    1) The main program is authorizer.py and to invoke it you should use Python.
        It receives json lines as input through stdin
        There are sample files in the operations directory with json data that can be used as input.

        Examples:

            $ python authorizer.py < operations/acc_already_init_op
                {"account": {"active-card": true, "available-limit": 175}, "violations": []}
                {"account": {"active-card": true, "available-limit": 175}, "violations": ["account-already-initialized"]}

            $ python3 authorizer.py < operations/trx_no_high_freq_error_op
                {"account": {"active-card": true, "available-limit": 1000}, "violations": []}
                {"account": {"active-card": true, "available-limit": 1000}, "violations": ["insufficient-limit"]}
                {"account": {"active-card": true, "available-limit": 1000}, "violations": ["insufficient-limit"]}
                {"account": {"active-card": true, "available-limit": 200}, "violations": []}
                {"account": {"active-card": true, "available-limit": 120}, "violations": []}

    1) To execute all test cases, run
        $  python3 -m pytest tests

Architecture
    An Hexagonal Architecture (aka ports and adapters) was used for this application.
    There's an adapter for the DB. In this case was only an in-memory DB.
    There's a port for the JSON API which is the one that currently this application can handle.
    All the business logic is inside the domain directory.
    With this architecture it should be noted that the port and the adapter depend on the domain, and not the other way around.
    Therefore, it should be flexible enough to receive other kinds of adapters and ports.




