import os
import sys

# Ensure Vercel can resolve top-level `app.` imports seamlessly
sys.path.insert(0, os.path.dirname(__file__))

from app.main import app
