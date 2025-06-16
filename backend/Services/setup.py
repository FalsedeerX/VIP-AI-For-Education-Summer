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
        "starlette==0.46.2",
        "fastapi==0.115.12",
        "pydantic==2.11.7",
        "pydantic_core==2.33.2"
    ]
)
