from setuptools import setup, find_packages

VERSION = '0.1.0'
DESCRIPTION = 'sqlalchemy-inspect'
LONG_DESCRIPTION = 'Get your database schema into your SQLAlchemy model'

# Setting up
setup(
    name="sqlalchemy-inspect",
    version=VERSION,
    author="Bruno Nascimento",
    author_email="<bruno_nascimento_89@hotmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    url='https://github.com/brunonascimento89/sqlalchemy-inspect',
    packages=find_packages(),
    install_requires=['python-decouple', 'SQLAlchemy', 'PyMySQL'],
    keywords=['python', 'sqlalchemy_inspect', 'sqlalchemy-inspect', 'sqlalchemy inspect','sqlalchemy', 'inspect', 'SQL', 'MySQL', 'SQLite'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)