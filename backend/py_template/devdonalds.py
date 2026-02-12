from dataclasses import dataclass
from typing import List, Dict, Union
from flask import Flask, request, jsonify
import re
RECIPEAMT = 1
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
	result = re.sub(r"[_-]", r" ", recipeName)
	result = re.sub(r"[^a-zA-Z ]", r"", result)
	result = result.split(" ")
	newRecipeName = []

	for word in result:
		word = word.lower().capitalize()
		newRecipeName.append(word)
	newRecipeName = " ".join(newRecipeName)

	if len(recipeName) <= 0:
		return None
	return newRecipeName


# [TASK 2] ====================================================================
# Endpoint that adds a CookbookEntry to your magical cookbook
@app.route('/entry', methods=['POST'])
def create_entry():
	entryData = request.get_json()
	entryDataClass = entryData["type"]
	if entryDataClass != "recipe" and entryDataClass != "ingredient":
		return jsonify({}), 400
	
	if entryDataClass == "ingredient":
		if entryData["cookTime"] < 0:
			return jsonify({}), 400
		
		if "requiredItems" in entryData:
			return jsonify({}), 400

	if entryDataClass == "recipe":
		if "cookTime" in entryData:
			return jsonify({}), 400

		# Checking for duplicate required items
		itemList = []
		for reqItem in entryData["requiredItems"]:
			if reqItem["name"] not in itemList:
				itemList.append(reqItem["name"])
			else:
				return jsonify({}), 400

	if entryData["name"] in cookbook:
		return jsonify({}), 400
	
	cookbook[entryData["name"]] = entryData
	return jsonify({}), 200


# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name
@app.route('/summary', methods=['GET'])
def summary():
	ingredientList = {}
	totalCookTime = 0

	# recursively goes through each requiredItem for a recipe
	def validSummary(name, multiplier):
		nonlocal totalCookTime
		nonlocal ingredientList

		if name not in cookbook:
			return False

		entry = cookbook[name]
		if entry["type"] == "ingredient":
			if name not in ingredientList:
				ingredientList[name] = multiplier
			else:
				ingredientList[name] += multiplier

			totalCookTime += multiplier * entry["cookTime"]
			return True
		elif entry["type"] != "recipe":
			return False
		
		for reqItem in entry["requiredItems"]:
			reqItemName, reqItemAmt = reqItem["name"], reqItem["quantity"]
			if not validSummary(reqItemName, reqItemAmt * multiplier):
				return False

		return True

	recipeName = request.args.get("name")
	if recipeName not in cookbook:
		return jsonify({}), 400

	entry = cookbook[recipeName]
	if entry["type"] == "ingredient":
		return jsonify({}), 400
	if not validSummary(recipeName, RECIPEAMT):
		return jsonify({}), 400
		
	finalIngredientList = []
	for name, quantity in ingredientList.items():
		finalIngredientList.append({
			"name": name,
			"quantity": quantity
		})

	return jsonify({
		"name": recipeName,
		"cookTime": totalCookTime,
		"ingredients": finalIngredientList
	}), 200



# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
