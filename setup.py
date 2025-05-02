# Copyright 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# setup.py is the fallback installation script when pyproject.toml does not work
from setuptools import setup, find_packages
import os
import re

# Read the version from the __init__.py file
with open(os.path.join("remedy", "__init__.py"), encoding="utf-8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

# Read the README for the long description
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="remedy",
    version=version,
    description="A framework for building conversational agents with event monitoring capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Remedy Team",
    author_email="team@remedy.ai",
    url="https://github.com/Jiayi-Pan/TinyZero",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0.0",
        "vllm<=0.6.3",
        "ray>=2.6.3",
        "flash-attn",
        "wandb",
        "matplotlib",
        "IPython",
        "transformers<4.48",
        "accelerate",
        "datasets",
    ],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8",
            "mypy"
        ],
        "mobile": [
            "firebase-admin",
            "twilio",
            "sendgrid",
        ]
    },
    python_requires=">=3.9,<3.10",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="llm, reinforcement-learning, event-monitoring, conversational-ai",
)