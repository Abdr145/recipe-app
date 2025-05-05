from flask import Blueprint, render_template, request
from app.models import Recipe

main_bp = Blueprint('main', __name__, template_folder='templates/main')

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    query = request.args.get('q', '')
    if query:
        recipes = Recipe.query.filter(Recipe.title.ilike(f'%{query}%')).all()
    else:
        recipes = Recipe.query.order_by(Recipe.date_posted.desc()).limit(5).all()
    return render_template('main/index.html', recipes=recipes, query=query)
