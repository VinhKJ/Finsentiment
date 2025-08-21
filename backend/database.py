from flask_sqlalchemy import SQLAlchemy

# Shared SQLAlchemy database instance
# Initialized without app to avoid circular imports
# Other modules should import `db` from this module

db = SQLAlchemy()
