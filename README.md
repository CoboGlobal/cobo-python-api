# The Official Python SDK for Cobo WaaS API

[![pypi](https://img.shields.io/pypi/v/cobo-custody.svg)](https://pypi.python.org/pypi/cobo-custody)
[![License: GPL v2](https://img.shields.io/badge/License-GPL_v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![GitHub Release](https://img.shields.io/github/release/CoboGlobal/cobo-python-api.svg?style=flat)]()

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

### Code Sample


#### Generate Key Pair

```python
from cobo_custody.signer.local_signer import generate_new_key
api_secret, api_key = generate_new_key()
print(api_secret)
print(api_key)
```

For more information on the API key, please [click here](https://www.cobo.com/developers/api-references/overview/authentication).


#### Initialize ApiSigner

`ApiSigner` can be instantiated through 

```python
from cobo_custody.signer.local_signer import LocalSigner
LocalSigner("API_SECRET")
```

In certain scenarios, the private key may be restricted from export, such as when it is stored in AWS Key Management Service (KMS). 
In such cases, please pass in a custom implementation using the ApiSigner interface:

#### Initialize RestClient

```python
from cobo_custody.client import Client
from cobo_custody.config import DEV_ENV
from cobo_custody.signer.local_signer import LocalSigner
client = Client(signer=signer, env=DEV_ENV, debug=True)
```

#### Complete Code Sample
```python
from cobo_custody.signer.local_signer import generate_new_key
from cobo_custody.client import Client
from cobo_custody.config import DEV_ENV
from cobo_custody.signer.local_signer import LocalSigner
api_secret, api_key = generate_new_key()
singer = LocalSigner("api_secret")
client = Client(signer=singer, env=DEV_ENV, debug=True)
res = client.get_account_info()
print(res)
```

