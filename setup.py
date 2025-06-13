from setuptools import setup, find_packages

setup(
    name="ragfant",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'streamlit',
        'openai',
        'python-dotenv',
        'requests',
        'faiss-cpu',
        'numpy',
        'pandas',
        'tqdm',
    ],
)