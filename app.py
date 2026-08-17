from flask import Flask, render_template, request
import math

app = Flask(__name__)

TAX_RATE = 0.15 
LABOR_HOURLY_RATE = 20.00
MARKUP_PERCENTAGE = 3.00

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

unit_conversions = {
    'gram': 1.0, 'kilogram': 1000.0, 'pound': 453.592, 'ounce': 28.35,
    'milliliter': 1.0, 'liter': 1000.0, 'fluid_ounce': 29.5735, 'cup': 236.588,
    'tablespoon': 14.7868, 'teaspoon': 4.92892, 'each': 1.0
}

def standardize_ingredient_costs(ingredients_list, conversions):
    for item in ingredients_list:
        purchase_unit = item['purchase_unit']
        conversion_rate = conversions.get(purchase_unit, 1.0)
        total_base_units = item['purchase_quantity'] * conversion_rate
        if total_base_units > 0:
            item['standard_cost'] = item['purchase_cost'] / total_base_units
    return ingredients_list

ingredients = standardize_ingredient_costs(ingredients, unit_conversions)

@app.route('/', methods=['GET', 'POST'])
def home():
    report = None
    if request.method == 'POST':
        recipe_name = request.form.get('recipe_name', 'Custom Recipe')
        batch_size = float(request.form.get('batch_size', 1))
        labor_minutes = float(request.form.get('labor_minutes', 0))
        
        selected_ingredients = request.form.getlist('ingredient_name')
        quantities = request.form.getlist('ingredient_qty')
        units = request.form.getlist('ingredient_unit')
        
        ingredients_map = {item['name']: item for item in ingredients}
        
        detailed_costs = []
        items_subtotal = 0.0
        total_tax = 0.0
        
        for name, qty_str, unit in zip(selected_ingredients, quantities, units):
            if name in ingredients_map and qty_str:
                qty = float(qty_str)
                db_item = ingredients_map[name]
                cost_per_unit = db_item['standard_cost']
                recipe_unit_conversion = unit_conversions.get(unit, 1.0)
                line_cost = qty * recipe_unit_conversion * cost_per_unit
                line_tax = line_cost * TAX_RATE if db_item['is_taxable'] else 0.0
                
                items_subtotal += line_cost
                total_tax += line_tax
                detailed_costs.append({'name': name, 'quantity': qty, 'unit': unit, 'cost': round(line_cost, 2)})
        
        labor_cost = (LABOR_HOURLY_RATE / 60) * labor_minutes
        total_recipe_cost = items_subtotal + total_tax + labor_cost
        cost_per_serving = total_recipe_cost / batch_size if batch_size > 0 else 0
        recommended_selling_price = cost_per_serving * (1 + MARKUP_PERCENTAGE)
        
        report = {
            'recipe_name': recipe_name,
            'line_items': detailed_costs,
            'items_subtotal': round(items_subtotal, 2),
            'total_tax': round(total_tax, 2),
            'labor_cost': round(labor_cost, 2),
            'total_recipe_cost': round(total_recipe_cost, 2),
            'cost_per_serving': round(cost_per_serving, 2),
            'recommended_selling_price': round(recommended_selling_price, 2)
        }
        
    return render_template('index.html', ingredients=ingredients, report=report)

if __name__ == '__main__':
    app.run(debug=True)
