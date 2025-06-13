from setuptools import setup, find_packages

setup(
    name="ragfant",
    version="0.1",
    packages=find_packages(),
    python_requires='>=3.9,<3.14',
    install_requires=[
        'streamlit==1.31.0',
        'openai==1.12.0',
        'python-dotenv==1.0.0',
        'requests==2.31.0',
        'numpy>=1.24.0,<1.25.0',
        'pandas>=1.5.0,<1.6.0',
        'sentence-transformers==2.2.2',
        'scipy>=1.9.0,<2.0.0',
        'scikit-learn>=1.2.0,<1.3.0',
        'rich>=10.14.0,<14.0.0',
        'protobuf>=3.20.0,<4.0.0'
    ]
)
)