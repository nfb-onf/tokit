from setuptools import setup, find_packages

setup(
    name = "tokit",
    version = "0.3",
    packages=find_packages(),
    package_data = {'' : ['fixtures/*.json']},
    install_requires =[],
    author = "NFB-ONF",
    author_email = "DevEquipeWeb@nfb.ca",
    description = "Tokit - Django application which manage to generation and validation of unique keys(tokens).",
    license = "new BSD",
    keywords = "",
    url = "http://nfb.ca/",  
)
