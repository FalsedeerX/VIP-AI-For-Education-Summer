from setuptools import setup, find_packages

setup(
    name="DatabaseAgent",
    version="0.1.0",
    author="VIP",
    description="PostgreSQL Database Broker",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.7",
    install_requires=[
        "argon2-cffi==23.1.0",
        "argon2-cffi-bindings==21.2.0",
        "psycopg==3.2.9",
        "psycopg-binary==3.2.9",
        "psycopg-pool==3.2.6",
        "python-dotenv==1.1.0",
    ]
)
