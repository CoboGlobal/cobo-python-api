from setuptools import find_packages, setup

with open("requirements.txt", "r") as f:
    requires = [x.strip() for x in f if x.strip()]

setup(
    name="cobo-python-api",
    version="0.3",
    author="Cobo",
    author_email="support@cobo.com",
    description="Cobo Custody restful api",
    license="Cobo Copyright Reserved",
    url="https://github.com/CoboCustody/cobo-python-api",
    include_package_data=True,
    install_requires=requires,
    # zip_safe=False,
)
