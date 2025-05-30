# app/ai_service.py
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from app.models import Recipe, Ingredient


class RecipeRecommendationService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', lowercase=True)
        self.recipe_vectors = None
        self.recipes = []

    def preprocess_ingredients(self, ingredients_text):
        """Clean and preprocess ingredient text"""
        # Remove measurements and common cooking terms
        cleaned = re.sub(
            r'\d+\.?\d*\s*(cup|cups|tablespoon|tablespoons|teaspoon|teaspoons|pound|pounds|ounce|ounces|gram|grams|kg|lb|tsp|tbsp|oz)\s*',
            '', ingredients_text.lower())
        cleaned = re.sub(r'\b(of|and|or|with|without|fresh|dried|chopped|sliced|diced|minced)\b', '', cleaned)
        cleaned = re.sub(r'[^\w\s]', ' ', cleaned)  # Remove punctuation
        cleaned = ' '.join(cleaned.split())  # Remove extra spaces
        return cleaned

    def build_recipe_database(self):
        """Build the recipe database for similarity matching"""
        recipes = Recipe.query.all()
        self.recipes = []
        recipe_texts = []

        for recipe in recipes:
            # Combine ingredients into text
            ingredients_text = ' '.join([ing.name for ing in recipe.ingredients])
            processed_text = self.preprocess_ingredients(ingredients_text)

            self.recipes.append({
                'id': recipe.id,
                'title': recipe.title,
                'description': recipe.description,
                'ingredients': [ing.name for ing in recipe.ingredients],
                'categories': [cat.name for cat in recipe.categories],
                'author': recipe.author.username,
                'image_file': recipe.image_file
            })
            recipe_texts.append(processed_text)

        if recipe_texts:
            self.recipe_vectors = self.vectorizer.fit_transform(recipe_texts)

    def find_recipes_by_ingredients(self, available_ingredients, max_results=10):
        """Find recipes that can be made with available ingredients"""
        if not self.recipe_vectors or not available_ingredients:
            return []

        # Preprocess user ingredients
        user_ingredients = self.preprocess_ingredients(' '.join(available_ingredients))

        try:
            # Transform user ingredients to vector
            user_vector = self.vectorizer.transform([user_ingredients])

            # Calculate similarity
            similarities = cosine_similarity(user_vector, self.recipe_vectors).flatten()

            # Get top matches
            top_indices = similarities.argsort()[-max_results:][::-1]

            results = []
            for idx in top_indices:
                if similarities[idx] > 0:  # Only include recipes with some similarity
                    recipe = self.recipes[idx].copy()
                    recipe['similarity_score'] = float(similarities[idx])
                    recipe['matching_ingredients'] = self._get_matching_ingredients(
                        available_ingredients, recipe['ingredients']
                    )
                    recipe['missing_ingredients'] = self._get_missing_ingredients(
                        available_ingredients, recipe['ingredients']
                    )
                    results.append(recipe)

            return results
        except Exception as e:
            print(f"Error in ingredient matching: {e}")
            return []

    def _get_matching_ingredients(self, available, recipe_ingredients):
        """Get ingredients that match between available and recipe"""
        available_lower = [ing.lower().strip() for ing in available]
        matching = []

        for recipe_ing in recipe_ingredients:
            recipe_ing_lower = recipe_ing.lower().strip()
            for avail_ing in available_lower:
                if avail_ing in recipe_ing_lower or recipe_ing_lower in avail_ing:
                    matching.append(recipe_ing)
                    break

        return matching

    def _get_missing_ingredients(self, available, recipe_ingredients):
        """Get ingredients missing from available ingredients"""
        available_lower = [ing.lower().strip() for ing in available]
        missing = []

        for recipe_ing in recipe_ingredients:
            recipe_ing_lower = recipe_ing.lower().strip()
            is_available = False

            for avail_ing in available_lower:
                if avail_ing in recipe_ing_lower or recipe_ing_lower in avail_ing:
                    is_available = True
                    break

            if not is_available:
                missing.append(recipe_ing)

        return missing


# Global instance
recommendation_service = RecipeRecommendationService()