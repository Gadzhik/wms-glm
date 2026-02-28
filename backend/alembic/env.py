"""Alembic environment configuration"""
from logging.config import fileConfig
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import Base
from app.models import *  # Import all models

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = fileConfig(os.path.join(os.path.dirname(__file__), "alembic.ini"))

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.has_section("loggers"):
    fileConfig(config.file).read(config.file)

# add your model's MetaData object here
# for 'autogenerate support'
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# etc.
