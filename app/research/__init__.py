from flask import Blueprint
research_bp = Blueprint('research', __name__)
from . import routes
