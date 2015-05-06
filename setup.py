from distutils.core import setup
setup(
    name="vsdcli",
    version="0.1.0",
    description="CLI for Nuage VSD",
    author="Maxime Terras",
    author_email="maxime.terras@numergy.com",
    scripts=["vsdcli"],
    py_modules=["nuage"],
    install_requires=["click", "prettytable"]
)
