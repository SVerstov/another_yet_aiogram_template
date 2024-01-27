# Overview
Aiogram template for scalable bot. 
Database - postrges/sqlite 
Migrations - alembic
Storage/cache - redis
Tests - pytest
Logging - loguru

# Setup
Before start be sure you have a poetry https://python-poetry.org/

# Config system
## Overview
The configuration system is designed to be flexible and easily extensible. All configurations are validated by pydantic..
All config except logger settings collected in one class `Config` in `config.py` file.

## Usage
An instance of `Config` is loaded in aiogram middleware. So you can use it in any handler out of the box.
In some cases you can manually load config `config = Config()`

## Add new config parameter
go to `config.py` and add parameter annotation to some branch:
```python
class BotConfig(ConfigBranch):
    your_new_parameter: str
```
after that go to `config.toml` and define your_new_parameter:
```toml
[bot]
your_new_parameter = "perfect template!"
```
Great! Now you can use it in your code:
`config.bot.your_new_parameter`

## Add new config branch
in `config.py`:
- create new class inherit from ConfigBranch
- make parameters annotations
- add new class to a `Config` class
in `config.toml`
- create new block using `[]`
- define parameters

*block name in toml must be the same as name in Config class*

# Logger
There is a preconfigured logging system in this project using *loguru*
The main idea is to create a separate log file for every module (folder in a root) in your project. 
You can find log files in `logs` folder


## Usage example
In bot/*.py
```python
from loguru import logger
logger.info("This is an info message")
```
log will be written in `bot.log`

## Logging configuration
Open `logger.toml`.

First of all configure `[base_config]`. 

Other blocks except `[console]` inherit `[base_config]` but you can overwrite what you want in specific module settings
You can add any loguru parameters. The list is here: https://loguru.readthedocs.io/en/stable/api/logger.html

## Add new module
It is simple:
- add new block in `logger.toml`. Be sure that a new block name is the same as your folder name.
- define file

## Write log to the another module
If you want to write logs from a different module than the one you are currently working in, you can use the `bind()` method to specify the target module. 
This allows you to direct the log output to a specific log file associated with that module
```python
from loguru import logger
pay_logger = logger.bind(name='payments')
# Don't forget to configure [payments] in toml file
pay_logger.info('This log will be written in payments.log')
```

## All logger
This logger collect all log messages. You can delete it if your want.