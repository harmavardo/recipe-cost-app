# File: app.py
from flask import Flask, render_template, request
import math

# --- App Configuration ---
TAX_RATE = 0.15 
LABOR_HOURLY_RATE = 20.00
MARKUP_PERCENTAGE = 3.00

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Data Tables ---
ingredients = [
    {'name': 'All-Purpose Flour', 'supplier': 'Bulk Barn', 'purchase_cost': 5.00, 'purchase_quantity': 2000, 'purchase_unit': 'gram', 'is_taxable': False},
    {'name': 'White Sugar', 'supplier': 'Costco', 'purchase_cost': 4.50, 'purchase_quantity': 10, 'purchase_unit': 'pound', 'is_taxable': False},
    {'name': 'Large Eggs', 'supplier': 'Local Farm', 'purchase_cost': 6.00, 'purchase_quantity': 12, 'purchase_unit': 'each', 'is_taxable': False},
    {'name': 'Unsalted Butter', 'supplier': 'Costco', 'purchase_cost': 7.50, 'purchase_quantity': 1, 'purchase_unit': 'pound', 'is_taxable': False},
    {'name': 'Vanilla Extract', 'supplier': 'Amazon', 'purchase_cost': 12.00, 'purchase_quantity': 8, 'purchase_unit': 'fluid_ounce', 'is_taxable': True},
    {'name': 'Yeast', 'supplier': 'Bulk Barn', 'purchase_cost': 10.00, 'purchase_quantity': 454, 'purchase_unit': 'gram', 'is_taxable': False},
    {'name': 'Salt', 'supplier': 'Bulk Barn', 'purchase_cost': 2.00, 'purchase_quantity': 1000, 'purchase_unit': 'gram', 'is_taxable': False}
]
supplies = [
    {'name': '8-inch Cake Box', 'supplier': 'Webstaurant Store', 'purchase_cost': 1.25, 'purchase_quantity': 1, 'unit': 'each', 'is_taxable': True},
    {'name': 'Cupcake Liners', 'supplier': 'Amazon', 'purchase_cost': 5.00, 'purchase_quantity': 100, 'unit': 'each', 'is_taxable': True},
    {'name': 'Parchment Paper Sheet', 'supplier': 'Costco', 'purchase_cost': 0.15, 'purchase_quantity': 1, 'unit': 'each', 'is_taxable': True},
    {'name': 'Pastry Bag', 'supplier': 'Amazon', 'purchase_cost': 15.00, 'purchase_quantity': 100, 'unit': 'each', 'is_taxable': True}
]
indirect_costs = [
    {'name': 'Oven Usage', 'cost_per_hour': 0.50},
    {'name': 'Mixer Usage', 'cost_per_hour': 0.10},
    {'name': 'Sheeter Usage', 'cost_per_hour': 0.75}
]
unit_conversions = {
    'gram': 1.0, 'kilogram': 1000.0, 'pound': 453.592, 'ounce': 28.35,
    'milliliter': 1.0, 'liter': 1000.0, 'fluid_ounce': 29.5735, 'cup': 236.588,
    'tablespoon': 14.7868, 'teaspoon': 4.92892, 'each': 1.0
}

# --- Helper Functions ---
def standardize_ingredient_costs(ingredients_list, conversions):
    for item in ingredients_list:
        purchase_unit = item['purchase_unit']
        conversion_rate = conversions.get(purchase_unit, 1.0)
        total_base_units = item['purchase_quantity'] * conversion_rate
        if total_base_units > 0:
            cost_per_base_unit = item['purchase_cost'] / total_base_units
            standard_unit = 'each'
            if any(u in purchase_unit for u in ['gram', 'pound', 'kilo', 'ounce']):
                standard_unit = 'gram'
            elif any(u in purchase_unit for u in ['liter', 'ounce', 'cup', 'tablespoon', 'teaspoon']):
                standard_unit = 'ml'
            item['standard_cost'] = cost_per_base_unit
            item['standard_unit'] = standard_unit
    return ingredients_list

def standardize_supply_costs(supplies_list):
    for item in supplies_list:
        if item['purchase_quantity'] > 0:
            item['cost_per_each'] = item['purchase_cost'] / item['purchase_quantity']
    return supplies_list

def calculate_indirect_costs_per_minute(costs_list):
    for cost_item in costs_list:
        cost_item['cost_per_minute'] = cost_item['cost_per_hour'] / 60
    return costs_list

ingredients = standardize_ingredient_costs(ingredients, unit_conversions)
supplies = standardize_supply_costs(supplies)
indirect_costs = calculate_indirect_costs_per_minute(indirect_costs)

# --- Routes ---
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
