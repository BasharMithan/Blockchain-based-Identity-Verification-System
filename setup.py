from setuptools import setup, find_packages

setup(
    name="Blockchain-based-Identity-Verification-System",
    author="Bashar Mithan",
    author_email="basharmithan@gmail.com",
    use_scm_version=True,
    setup_requires=["setuptools-scm"],
    packages=find_packages(where="source"),
    package_dir={"": "source"},
    python_requires=">=3.11",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
    ],
    
)
