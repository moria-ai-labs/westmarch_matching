from setuptools import setup, find_packages

setup(
    name="wordmatcher",
    version="0.1.0",
    packages=find_packages(where="."), # Adjusted to look in the current directory
    install_requires=[
        "rapidfuzz>=3.0.0", # Added rapidfuzz
    ],
    entry_points={
        "console_scripts": [
            # If you want to create any command-line tools
        ],
    },
    author="Your Name", # Replace with your name
    author_email="your.email@example.com", # Replace with your email
    description="A Python library to find the closest match for words from a given list.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https_github.com_yourusername_wordmatcher", # Replace with your project's URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License", # Choose an appropriate license
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
