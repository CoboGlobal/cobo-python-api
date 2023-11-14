# The Official Python SDK for Cobo WaaS API

[![pypi](https://img.shields.io/pypi/v/cobo-custody.svg)](https://pypi.python.org/pypi/cobo-custody)


## About
This repository contains the official Python SDK for Cobo WaaS API, enabling developers to integrate with Cobo's Custodial and/or MPC services seamlessly using the Python programming language.

## Documentation
To access the API documentation, navigate to the [API references](https://www.cobo.com/developers/api-references/overview/).

For more information on Cobo's Python SDK, refer to the [Python SDK Guide](https://www.cobo.com/developers/get-started/sdks/waas/python).

## Usage

### Before You Begin
Ensure that you have created an account and configured Cobo's Custodial and/or MPC services. 
For detailed instructions, please refer to the [Quickstart](https://www.cobo.com/developers/get-started/overview/quickstart) guide.

### Requirements
Python 3.7 or newer.

### Installation
The source code is only required for those looking to modify the package.   
If you just want to use it, please run the following commands:

```sh
pip install --upgrade cobo-custody
```

Install from source with:

```sh
python setup.py install
```

### Importing Cobo SDK
```python
from cobo_custody.signer.local_signer import generate_new_key
from cobo_custody.client import Client
from cobo_custody.config import DEV_ENV
from cobo_custody.signer.local_signer import LocalSigner
api_secret, api_key = generate_new_key()
singer = LocalSigner("api_secret")
client = Client(signer=singer, env=DEV_ENV, debug=True)
client.get_account_info()
```

