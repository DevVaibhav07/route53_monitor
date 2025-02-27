from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="route53-monitor",
    version="1.0.0",
    author="Vaibhav Kubade",
    author_email="vaibhav.kubade@juspay.in",
    description="A monitoring system for AWS Route53 DNS changes with Slack notifications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vaibhavkubade/route53-monitor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: System :: Monitoring",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "boto3>=1.26.0",
        "python-dotenv>=0.19.0",
        "requests>=2.26.0"
    ],
    entry_points={
        "console_scripts": [
            "route53-monitor=route53_monitor:main",
        ],
    },
) 