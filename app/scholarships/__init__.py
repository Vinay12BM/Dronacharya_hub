from flask import Blueprint

scholarship_bp = Blueprint('scholarships', __name__)

from . import routes
