from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="trading-bot-ema",
    version="1.0.0",
    author="Morcimer",
    description="EMA-Momentum Trading Bot with FastAPI interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Morcimer/tradingBot",
    project_urls={
        "Bug Tracker": "https://github.com/Morcimer/tradingBot/issues",
        "Documentation": "https://github.com/Morcimer/tradingBot/blob/main/README.md",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.14",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "trading-bot=main:main",
        ],
    },
)
