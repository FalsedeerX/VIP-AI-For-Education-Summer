from setuptools import setup, find_packages

setup(
    name="SessionManager",
    version="0.1.0",
    author="VIP",
    description="Valkey Database Broker",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.7",
    install_requires=[
        "redis==6.2.0"
    ]
)
