from flask import Blueprint, render_template, request, redirect, url_for
from app.models import Recipe
from app.recipes.forms import IngredientSearchForm
from app.ai_service import recommendation_service

main_bp = Blueprint('main', __name__, template_folder='templates/main')


@main_bp.route('/', methods=['GET', 'POST'])
def index():
    search_form = IngredientSearchForm()
    query = request.args.get('q', '')

    # Handle ingredient-based search
    if search_form.validate_on_submit():
        ingredients = [ing.strip() for ing in search_form.ingredients.data.split(',') if ing.strip()]
        return redirect(url_for('main.ingredient_search', ingredients=','.join(ingredients)))

    # Handle regular text search
    if query:
        recipes = Recipe.query.filter(Recipe.title.ilike(f'%{query}%')).all()
    else:
        recipes = Recipe.query.order_by(Recipe.date_posted.desc()).limit(8).all()

    return render_template('main/index.html', recipes=recipes, query=query, search_form=search_form)


@main_bp.route('/ingredient-search')
def ingredient_search():
    ingredients_param = request.args.get('ingredients', '')

    if not ingredients_param:
        return redirect(url_for('main.index'))

    ingredients = [ing.strip() for ing in ingredients_param.split(',') if ing.strip()]

    # Rebuild recipe database (in production, this should be cached)
    recommendation_service.build_recipe_database()

    # Get recipe recommendations
    suggested_recipes = recommendation_service.find_recipes_by_ingredients(ingredients, max_results=15)

    return render_template('main/ingredient_search.html',
                           suggested_recipes=suggested_recipes,
                           ingredients=ingredients)