
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect


# Manage user login sessions
login_manager = LoginManager()

login_manager.login_view = "auth.login"
login_manager.login_message = "Please sign in to access VAULTEX."
login_manager.login_message_category = "info"


# Protect forms against Cross-Site Request Forgery (CSRF)
csrf = CSRFProtect()
