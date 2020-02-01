import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = 'jokettttbot',
    packages = setuptools.find_packages(),
    version = '1.0.0',
    license = 'MIT',
    author = 'Francesco Piantini',
    author_email = 'francesco.piantini@gmail.com',
    description = 'A Telegram bot that plays tic-tac-toe',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/fpiantini/jokettt_tbot',
    download_url = 'https://github.com/fpiantini/jokettt_tbot/archive/v1.0.0.tar.gz',
    install_requires=[
          'numpy',
          'babel',
          'python-telegram-bot',
          'jokettt',
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
    ],
    python_requires='>=3.6',
)

