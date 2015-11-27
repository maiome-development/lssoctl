try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

import lssoctl

setup(
    name = "lssoctl",
    version = lssoctl.__version__,
    description = "Command line interface to LSSO.",
    url = "https://phabricator.ramcloud.io/tag/lssoctl",
    author = "Sean Johnson",
    author_email = "sean.johnson@maio.me",

    license = "MIT",

    classifiers = [
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
    ],

    packages = [
        "lssoctl",
        "lssoctl.cmd",
        "lssoctl.util",
    ],

    package_dir = {
        "lssoctl": "lssoctl",
    },

    zip_safe = True,
    entry_points = {
        "console_scripts": [
            "lssoctl = lssoctl.cmd.console:command_main",
        ],
    }
)
