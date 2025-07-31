from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="website_rag_crawler",
    version="0.1.0",
    description="Website crawler for RAG-powered Q&A system",
    author="RAG Q&A Team",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.8",
)