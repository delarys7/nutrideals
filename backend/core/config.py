"""
Configuration Module for NutriDeals Backend
Loads environment variables from .env
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file at project root
env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(dotenv_path=os.path.abspath(env_path))

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is missing in .env")
