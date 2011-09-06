from setuptools import setup, find_packages
setup(
    name = "tokit",
    version = "0.1",
    packages=find_packages(),
    package_data = {'fixtures':['*.json']},
    install_requires =['South==0.7.1'],
#    package_dir = {'':'src'},
#    scripts = ['say_hello.py'],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
#    install_requires = ['docutils>=0.3'],
#
#    package_data = {
#        # If any package contains *.txt or *.rst files, include them:
#        '': ['*.txt', '*.rst'],
#        # And include any *.msg files found in the 'hello' package, too:
#        'hello': ['*.msg'],
#    }

    # metadata for upload to PyPI
    author = "NFB-ONF",
    author_email = "DevEquipeWeb@nfb.ca",
    description = "tokit Package",
    license = "PSF",
    keywords = "",
    url = "http://nfb.ca/",   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.
)
