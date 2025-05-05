import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from app import db
from app.models import Recipe, Ingredient, Category, Comment
from app.recipes.forms import RecipeForm, CommentForm
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

recipes_bp = Blueprint('recipes', __name__, template_folder='templates/recipes')

def save_image(image):
    filename = secure_filename(image.filename)
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    image.save(path)
    return filename

@recipes_bp.route('/recipes')
def list_recipes():
    recipes = Recipe.query.order_by(Recipe.date_posted.desc()).all()
    return render_template('recipes/list.html', recipes=recipes)

@recipes_bp.route('/recipe/<int:recipe_id>', methods=['GET', 'POST'])
def recipe_detail(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, author=current_user, recipe=recipe)
        db.session.add(comment)
        db.session.commit()
        flash('Comment added.', 'success')
        return redirect(url_for('recipes.recipe_detail', recipe_id=recipe.id))
    return render_template('recipes/detail.html', recipe=recipe, form=form)

@recipes_bp.route('/recipe/new', methods=['GET', 'POST'])
@login_required
def new_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        filename = None
        if form.image.data:
            filename = save_image(form.image.data)
        recipe = Recipe(
            title=form.title.data,
            description=form.description.data,
            instructions=form.instructions.data,
            image_file=filename,
            author=current_user
        )
        # Ingredients
        for name in form.ingredients.data.split(','):
            ing = Ingredient.query.filter_by(name=name.strip()).first()
            if not ing:
                ing = Ingredient(name=name.strip())
            recipe.ingredients.append(ing)
        # Categories
        for name in form.categories.data.split(','):
            cat = Category.query.filter_by(name=name.strip()).first()
            if not cat:
                cat = Category(name=name.strip())
            recipe.categories.append(cat)
        db.session.add(recipe)
        db.session.commit()
        flash('Recipe created.', 'success')
        return redirect(url_for('recipes.list_recipes'))
    return render_template('recipes/form.html', form=form)

@recipes_bp.route('/recipe/<int:recipe_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.author != current_user:
        flash('You cannot edit this recipe.', 'danger')
        return redirect(url_for('recipes.list_recipes'))
    form = RecipeForm(obj=recipe)
    if form.validate_on_submit():
        recipe.title = form.title.data
        recipe.description = form.description.data
        recipe.instructions = form.instructions.data
        if form.image.data:
            recipe.image_file = save_image(form.image.data)
        # Update ingredients and categories alike above...
        db.session.commit()
        flash('Recipe updated.', 'success')
        return redirect(url_for('recipes.recipe_detail', recipe_id=recipe.id))
    form.ingredients.data = ', '.join([i.name for i in recipe.ingredients])
    form.categories.data = ', '.join([c.name for c in recipe.categories])
    return render_template('recipes/form.html', form=form)

@recipes_bp.route('/recipe/<int:recipe_id>/delete', methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.author != current_user:
        flash('You cannot delete this recipe.', 'danger')
        return redirect(url_for('recipes.list_recipes'))
    db.session.delete(recipe)
    db.session.commit()
    flash('Recipe deleted.', 'success')
    return redirect(url_for('recipes.list_recipes'))
