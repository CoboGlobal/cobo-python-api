from setuptools import setup
setup(
    name="cobo_custody",
    version="0.19",
    author="Cobo",
    author_email="support@cobo.com",
    description="Cobo Custody restful api",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="Cobo Copyright Reserved",
    python_requires=">=3.7",
    url="https://github.com/CoboCustody/cobo-python-api",
    packages=['cobo_custody', 'cobo_custody.model','cobo_custody.signer', 'cobo_custody.client', 'cobo_custody.error', 'cobo_custody.config'],
    include_package_data=True,
    install_requires=["ecdsa==0.17.0", "requests"]
    # zip_safe=False,
)
