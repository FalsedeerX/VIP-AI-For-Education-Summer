from setuptools import setup, find_packages

setup(
    name="Services",
    version="0.1.0",
    author="VIP",
    description="FastAPI Endpoints Implementation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.7",
    install_requires=[
        "fastapi==0.115.12",
        "uvicorn==0.34.3"
    ]
)
