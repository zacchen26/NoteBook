from setuptools import setup, find_packages

setup(
    name="AlphaNotebook",
    version="2.3",
    description="Knowledge-based search tool with BM25 ranking and NLP processing.",
    author="Zeyu Chen",
    packages=find_packages(),
    data_files=[('data', ['data/glove.6B.100d.txt'])],
    install_requires=[
        "spacy",
        "numpy",
        "rank_bm25",
        "sqlite3" 
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'alpha-search=alpha.search_engine_bot:main',
        ],
    },
)
