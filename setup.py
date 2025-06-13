from setuptools import setup, find_packages

setup(
    name="ragfant",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'streamlit==1.31.0',
        'openai==1.12.0',
        'python-dotenv==1.0.0',
        'requests==2.31.0',
        'pandas==1.5.3',
        'numpy==1.24.3',
        'torch==2.1.0+cpu',
        'torchvision==0.16.0+cpu',
        'torchaudio==2.1.0+cpu',
        'transformers==4.36.0',
        'tokenizers==0.15.0',
        'scikit-learn==1.2.2',
        'rich>=10.14.0,<14.0.0'
    ],
)