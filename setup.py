from setuptools import setup, find_packages
from src.version import get_version

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gitauto",
    version=get_version(),
    author="Gitty",
    author_email="gitty@example.com",
    description="A tool for automating Git operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/gitauto",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pytest",
        "flake8",
        "black",
        "mypy",
    ],
    entry_points={
        "console_scripts": [
            "gitauto=gitauto.main:main",
        ],
    },
)
