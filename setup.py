from setuptools import setup, find_packages

setup(
    name="hubqueue",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PyGithub",
        "click",
        "requests",
        "python-dotenv",
        "colorama",
        "tabulate",
        "tqdm",
    ],
    entry_points={
        "console_scripts": [
            "hubqueue=hubqueue.cli:main",
        ],
    },
    python_requires=">=3.8",
    author="",
    author_email="",
    description="A command-line interface for GitHub tools",
    keywords="github, cli, tools",
    url="",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
