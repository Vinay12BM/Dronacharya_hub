from flask import Blueprint

classroom_bp = Blueprint('classroom', __name__)

from . import routes
