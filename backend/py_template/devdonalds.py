from dataclasses import dataclass
from typing import List, Dict, Union
from flask import Flask, request, jsonify
import re

# ==== Type Definitions, feel free to add or modify ===========================
@dataclass
class CookbookEntry:
	name: str

@dataclass
class RequiredItem():
	name: str
	quantity: int

@dataclass
class Recipe(CookbookEntry):
	required_items: List[RequiredItem]

@dataclass
class Ingredient(CookbookEntry):
	cook_time: int


# =============================================================================
# ==== HTTP Endpoint Stubs ====================================================
# =============================================================================
app = Flask(__name__)

# Store your recipes here!
cookbook = {}

# Task 1 helper (don't touch)
@app.route("/parse", methods=['POST'])
def parse():
	data = request.get_json()
	recipe_name = data.get('input', '')
	parsed_name = parse_handwriting(recipe_name)
	if parsed_name is None:
		return 'Invalid recipe name', 400
	return jsonify({'msg': parsed_name}), 200

# [TASK 1] ====================================================================
# Takes in a recipeName and returns it in a form that 
def parse_handwriting(recipeName: str) -> Union[str | None]:
	recipeName = recipeName.replace("-", " ").replace("_", " ")
	
	notAlpha = re.compile('[^a-zA-Z ]')
	recipeName = notAlpha.sub('', recipeName)

	recipeName = recipeName.lower()
	recipeNameSplit = [word[0].upper() + word[1:] for word in recipeName.split()]
	recipeName = " ".join(recipeNameSplit)

	recipeName = re.sub(' +', ' ', recipeName).lstrip().rstrip()

	if len(recipeName) <= 0:
		return None
	return recipeName


# [TASK 2] ====================================================================
# Endpoint that adds a CookbookEntry to your magical cookbook
@app.route('/entry', methods=['POST'])
def create_entry():
	data = request.get_json()
	name = data.get('name', '')
	type = data.get('type', '')

	if len(name) <= 0 or len(type) <= 0:
		return 'invalid name / type', 400
	if name in cookbook:
		return 'entry names must be unique', 400

	if type == "recipe":
		requiredItems = data.get('requiredItems', [])
		requiredItemsDict = {}

		for item in requiredItems:
			item_name = item.get('name')
			item_quantity = item.get('quantity')
			if item_name in requiredItemsDict:
				return 'Recipe requiredItems can only have one element per name.', 400
			requiredItemsDict[item_name] = item_quantity

	elif type == "ingredient":
		cookTime = data.get('cookTime', -1)
		if cookTime < 0:
			return 'cookTime can only be greater than or equal to 0.', 400

	else:
		return 'type can only be "recipe" or "ingredient."', 400

	cookbook[name] = data
	return jsonify({}), 200


# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name
@app.route('/summary', methods=['GET'])
def summary():
	data = request.args
	name = data.get('name', '')
	
	if name not in cookbook:
		return 'A recipe with the corresponding name: ' + name + ' cannot be found.', 400
	
	entry = cookbook.get(name)
	entry_type = entry.get('type')
	if entry_type != "recipe":
		return 'The searched name is NOT a recipe name (ie. an ingredient).', 400
	
	ingredients = []
	cookTime = getCookTime(name, ingredients)
	if cookTime == -1:
		return 'Recipe contains items not in the cookbook', 400
			
	result = jsonify({
		'name': name,
		'cookTime': cookTime,
		'ingredients': ingredients
	})
	return result, 200

# Returns cookTime of recipe / ingredient, and adds ingredients to list
def getCookTime(name: str, ingredients: List) -> int:
	if name not in cookbook:
		return -1
	
	entry = cookbook.get(name)
	entry_type = entry.get('type')

	if entry_type == "ingredient":
		return entry.get('cookTime')
	else:
		cookTime = 0
		for item in entry.get('requiredItems'):
			itemCookTime = getCookTime(item.get('name'), ingredients)
			if itemCookTime == -1:
				return -1
			cookTime += (item.get('quantity') * itemCookTime)
			
			# handle final ingredient list
			if getType(item.get('name')) == "recipe":
				continue
			exists = False
			for ingredient in ingredients:
				if ingredient.get('name') == item.get('name'):
					ingredient['quantity'] += item.get('quantity')
					exists = True
			if not exists:
				ingredients.append({
					'name': item.get('name'),
					'quantity': item.get('quantity')
				})

	return cookTime

def getType(name: str) -> str:
	if name not in cookbook:
		return None
	elif cookbook.get(name).get('type') == "recipe":
		return "recipe"
	else:
		return "ingredient"

# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
