# Add this to app/recipes/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectMultipleField, FileField
from wtforms.validators import DataRequired

class RecipeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    instructions = TextAreaField('Instructions', validators=[DataRequired()])
    ingredients = StringField('Ingredients (comma-separated)', validators=[DataRequired()])
    categories = StringField('Categories (comma-separated)', validators=[DataRequired()])
    image = FileField('Image File')
    submit = SubmitField('Submit')

class CommentForm(FlaskForm):
    body = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Post Comment')

class IngredientSearchForm(FlaskForm):
    ingredients = StringField('Available Ingredients (comma-separated)',
                            validators=[DataRequired()],
                            render_kw={"placeholder": "tomato, onion, garlic, cheese..."})
    submit = SubmitField('Find Recipes')