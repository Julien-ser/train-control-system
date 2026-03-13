from setuptools import setup, find_packages

setup(
    name="train-control-system",
    version="0.1.0",
    description="A Python-based implementation demonstrating modern railway control systems",
    author="Train Control Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "pytest>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
