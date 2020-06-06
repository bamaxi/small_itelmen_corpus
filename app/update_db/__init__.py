from flask import Blueprint

bp = Blueprint('update', __name__)
from app.update_db import parse
