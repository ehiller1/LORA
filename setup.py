"""Setup script for RMN LoRA System."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="rmn-lora-system",
    version="1.0.0",
    author="RMN Team",
    description="Retail Media Network LoRA Optimization System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/rmn-lora-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "rmn-harmonize=src.agents.data_harmonizer:main",
            "rmn-plan=src.agents.planner:main",
            "rmn-optimize=src.agents.budget_optimizer:main",
            "rmn-train=src.training.train_lora:main",
            "rmn-serve=src.runtime.multi_tenant:main",
            "rmn-rlhf=src.ui.rlhf_app:main",
        ],
    },
)
