"""
Setup script para el proyecto
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="rosario-central-scraper",
    version="2.0.0",
    author="Francesco Camussoni",
    description="Scraper modular para obtener información histórica de jugadores de Rosario Central",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tu-usuario/rosario-central-scraper",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "carc-scrape=scripts.run_scraper:main",
            "carc-analyze=scripts.analyze_data:main",
        ],
    },
)
