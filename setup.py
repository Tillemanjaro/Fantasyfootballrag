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
        'faiss-cpu==1.7.4',
        'numpy==1.24.3',
        'pandas==2.0.3',
        'tqdm==4.66.1',
    ],
)