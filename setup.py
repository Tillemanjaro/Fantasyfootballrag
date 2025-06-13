from setuptools import setup, find_packages

setup(
    name="ragfant",
    version="0.1",
    packages=find_packages(),
    python_requires='>=3.9,<3.12',
    install_requires=[
        'streamlit==1.31.0',
        'openai==1.12.0',
        'python-dotenv==1.0.0',
        'requests==2.31.0',
        'numpy<2',
        'pandas<2',
        'scikit-learn<2',
        'torch==2.0.1+cpu',
        'transformers<5.0.0',
        'rich<14.0.0'
    ]
)
)