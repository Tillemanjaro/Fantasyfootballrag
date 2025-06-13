from setuptools import setup, find_packages

setup(
    name="ragfant",
    version="0.1",
    packages=find_packages(),
    python_requires='>=3.13',
    install_requires=[
        'streamlit==1.32.0',
        'openai==1.12.0',
        'python-dotenv==1.0.1',
        'requests==2.31.0',
        'numpy>=2.0.0rc1',  # Python 3.13 compatible version
        'pandas>=2.2.0rc0',  # Python 3.13 compatible version
        'scipy>=1.12.0rc1',  # Python 3.13 compatible version
        'rich==13.7.0'
    ]
)