# File: app.py
# Version: 2.0 - With Pricing and Labor
# Created: June 12, 2025
# Our complete code for the Recipe Cost & Pricing Calculator.

import math

# --- App Configuration (UPDATED) ---
# A central place for key business settings.
TAX_RATE = 0.15 # Based on 15% HST in New Brunswick
LABOR_HOURLY_RATE = 20.00 # The cost of labor per hour
MARKUP_PERCENTAGE = 3.00 # e.g., 3.00 means a 300% markup

# --- Data Tables (Ingredients, Supplies, etc.) ---
# ... (These tables remain the same as before) ...
# --- Table 1: Ingredients ---
ingredients = [
    {'name': 'All-Purpose Flour', 'supplier': 'Bulk Barn', 'purchase_cost': 5.00, 'purchase_quantity': 2000, 'purchase_unit': 'gram', 'is_taxable': False},
    {'name': 'White Sugar', 'supplier': 'Costco', 'purchase_cost': 4.50, 'purchase_quantity': 10, 'purchase_unit': 'pound', 'is_taxable': False},
    {'name': 'Large Eggs', 'supplier': 'Local Farm', 'purchase_cost': 6.00, 'purchase_quantity': 12, 'purchase_unit': 'each', 'is_taxable': False},
    {'name': 'Unsalted Butter', 'supplier': 'Costco', 'purchase_cost': 7.50, 'purchase_quantity': 1, 'purchase_unit': 'pound', 'is_taxable': False},
    {'name': 'Vanilla Extract', 'supplier': 'Amazon', 'purchase_cost': 12.00, 'purchase_quantity': 8, 'purchase_unit': 'fluid_ounce', 'is_taxable': True},
    {'name': 'Yeast', 'supplier': 'Bulk Barn', 'purchase_cost': 10.00, 'purchase_quantity': 454, 'purchase_unit': 'gram', 'is_taxable': False},
    {'name': 'Salt', 'supplier': 'Bulk Barn', 'purchase_cost': 2.00, 'purchase_quantity': 1000, 'purchase_unit': 'gram', 'is_taxable': False}
]
# --- Table 2: Supplies ---
supplies = [
    {'name': '8-inch Cake Box', 'supplier': 'Webstaurant Store', 'purchase_cost': 1.25, 'purchase_quantity': 1, 'unit': 'each', 'is_taxable': True},
    {'name': 'Cupcake Liners', 'supplier': 'Amazon', 'purchase_cost': 5.00, 'purchase_quantity': 100, 'unit': 'each', 'is_taxable': True},
    {'name': 'Parchment Paper Sheet', 'supplier': 'Costco', 'purchase_cost': 0.15, 'purchase_quantity': 1, 'unit': 'each', 'is_taxable': True},
    {'name': 'Pastry Bag', 'supplier': 'Amazon', 'purchase_cost': 15.00, 'purchase_quantity': 100, 'unit': 'each', 'is_taxable': True}
]
# --- Table 3: Indirect Costs ---
indirect_costs = [
    {'name': 'Oven Usage', 'cost_per_hour': 0.50},
    {'name': 'Mixer Usage', 'cost_per_hour': 0.10},
    {'name': 'Sheeter Usage', 'cost_per_hour': 0.75} # Added for croissants
]
# --- Table 4: Unit of Measure Conversions ---
unit_conversions = {
    'gram': 1.0, 'kilogram': 1000.0, 'pound': 453.592, 'ounce': 28.35,
    'milliliter': 1.0, 'liter': 1000.0, 'fluid_ounce': 29.5735, 'cup': 236.588,
    'tablespoon': 14.7868, 'teaspoon': 4.92892, 'each': 1.0
}

# --- Processing Functions (these remain the same) ---
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

# --- Run the Standardization on our Data ---
ingredients = standardize_ingredient_costs(ingredients, unit_conversions)
supplies = standardize_supply_costs(supplies)
indirect_costs = calculate_indirect_costs_per_minute(indirect_costs)

# --- NEW RECIPE EXAMPLE ---
# Using your "Croissant Roll" example.
croissant_recipe_inputs = {
    'batch_size': 12, # How many croissants this recipe makes
    'total_labor_minutes': 90, # Total active work time
    'items': [
        # type, name, quantity, unit
        {'type': 'ingredient', 'name': 'All-Purpose Flour', 'quantity': 500, 'unit': 'gram'},
        {'type': 'ingredient', 'name': 'Unsalted Butter', 'quantity': 300, 'unit': 'gram'},
        {'type': 'ingredient', 'name': 'White Sugar', 'quantity': 50, 'unit': 'gram'},
        {'type': 'ingredient', 'name': 'Yeast', 'quantity': 10, 'unit': 'gram'},
        {'type': 'ingredient', 'name': 'Salt', 'quantity': 10, 'unit': 'gram'},
        {'type': 'ingredient', 'name': 'Large Eggs', 'quantity': 1, 'unit': 'each'}, # For egg wash
        
        {'type': 'supply', 'name': 'Pastry Bag', 'quantity': 1, 'unit': 'each'},
        {'type': 'supply', 'name': 'Parchment Paper Sheet', 'quantity': 2, 'unit': 'each'},

        {'type': 'indirect_cost', 'name': 'Sheeter Usage', 'quantity': 15, 'unit': 'minute'},
        {'type': 'indirect_cost', 'name': 'Oven Usage', 'quantity': 18, 'unit': 'minute'},
    ]
}


# --- UPDATED CALCULATION ENGINE ---
def calculate_recipe_price(recipe_details, ingredients_db, supplies_db, indirect_costs_db, tax_rate, labor_rate, markup):
    
    # Extract details from the recipe input
    recipe_items = recipe_details['items']
    batch_size = recipe_details['batch_size']
    labor_minutes = recipe_details['total_labor_minutes']

    detailed_costs = []
    items_subtotal = 0.0
    total_tax = 0.0

    ingredients_map = {item['name']: item for item in ingredients_db}
    supplies_map = {item['name']: item for item in supplies_db}
    indirect_costs_map = {item['name']: item for item in indirect_costs_db}

    for item in recipe_items:
        # (This part of the loop is the same as before, calculating item & tax cost)
        line_cost = 0.0
        line_tax = 0.0
        item_name = item['name']
        if item['type'] == 'ingredient' and item_name in ingredients_map:
            db_item = ingredients_map[item_name]
            cost_per_unit = db_item['standard_cost']
            recipe_unit_conversion = unit_conversions.get(item['unit'], 1.0)
            line_cost = item['quantity'] * recipe_unit_conversion * cost_per_unit
            if db_item['is_taxable']: line_tax = line_cost * tax_rate
        elif item['type'] == 'supply' and item_name in supplies_map:
            db_item = supplies_map[item_name]
            line_cost = item['quantity'] * db_item['cost_per_each']
            if db_item['is_taxable']: line_tax = line_cost * tax_rate
        elif item['type'] == 'indirect_cost' and item_name in indirect_costs_map:
            db_item = indirect_costs_map[item_name]
            line_cost = item['quantity'] * db_item['cost_per_minute']
        
        items_subtotal += line_cost
        total_tax += line_tax
        detailed_costs.append({'name': item_name, 'cost': round(line_cost, 4)})

    # --- NEW: Perform final business calculations ---
    
    # Calculate total cost of labor for the recipe
    labor_cost = (labor_rate / 60) * labor_minutes
    
    # Calculate the total cost of the entire batch
    total_recipe_cost = items_subtotal + total_tax + labor_cost
    
    # Calculate the cost per final product/serving
    cost_per_serving = total_recipe_cost / batch_size
    
    # Calculate the final selling price based on the desired markup
    recommended_selling_price = cost_per_serving * (1 + markup)

    return {
        'line_items': detailed_costs,
        'items_subtotal': round(items_subtotal, 2),
        'total_tax': round(total_tax, 2),
        'labor_cost': round(labor_cost, 2),
        'total_recipe_cost': round(total_recipe_cost, 2),
        'cost_per_serving': round(cost_per_serving, 2),
        'recommended_selling_price': round(recommended_selling_price, 2)
    }

# --- Let's Run the Final Calculation! ---
final_price_report = calculate_recipe_price(
    croissant_recipe_inputs, ingredients, supplies, indirect_costs, 
    TAX_RATE, LABOR_HOURLY_RATE, MARKUP_PERCENTAGE
)

# --- UPDATED: Print a Full Business Report ---
print("--- Business Report: 12 Croissant Rolls ---")
print("\n--- 1. Cost Breakdown ---")
for item in final_price_report['line_items']:
    print(f"  Item: {item['name']:<25} Cost: ${item['cost']:<8.4f}")

print("\n--- 2. Financial Summary ---")
print(f"  Ingredients & Supplies Subtotal:      ${final_price_report['items_subtotal']:.2f}")
print(f"  Taxes:                                ${final_price_report['total_tax']:.2f}")
print(f"  Labor Cost:                           ${final_price_report['labor_cost']:.2f}")
print("-" * 50)
print(f"  TOTAL BATCH COST:                     ${final_price_report['total_recipe_cost']:.2f}")
print("-" * 50)

print("\n--- 3. Pricing Strategy ---")
print(f"  Cost per Croissant:                   ${final_price_report['cost_per_serving']:.2f}")
print(f"  Markup:                               {MARKUP_PERCENTAGE:.0%}")
print(f"  RECOMMENDED SELLING PRICE:            ${final_price_report['recommended_selling_price']:.2f}")
print("="*50)