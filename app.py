from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)
DB_FILE = 'database.json'

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {"ingredients": [], "packaging": [], "other": []}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def calculate_item_cost(item, qty):
    purchase_cost = item.get('purchase_cost', 0)
    purchase_qty = item.get('purchase_quantity', 1)
    if purchase_qty == 0:
        return 0.0
    unit_cost = purchase_cost / purchase_qty
    return unit_cost * qty

@app.route('/')
def home():
    db = load_db()
    return render_template('index.html', db=db)

@app.route('/calculate', methods=['POST'])
def calculate():
    db = load_db()
    data = request.json
    
    # Extract Base Dough Formula inputs
    pieces = float(data.get('pieces', 1))
    grams_per_piece = float(data.get('grams_per_piece', 0))
    total_target_dough = pieces * grams_per_piece
    
    mode = data.get('mode', 'percentage') # 'percentage' or 'grams'
    
    # Process Base Dough Ingredients
    raw_materials_db = {i['name']: i for i in db.get('ingredients', [])}
    dough_items = data.get('dough_ingredients', [])
    
    calculated_dough = []
    total_dough_weight = 0.0
    
    if mode == 'percentage':
        total_percentage = sum(float(item.get('pct', 0)) for item in dough_items)
        flour_weight = (total_target_dough / total_percentage * 100) if total_percentage > 0 else 0
        
        for item in dough_items:
            name = item.get('name')
            pct = float(item.get('pct', 0))
            weight = (flour_weight * pct / 100.0)
            db_item = raw_materials_db.get(name, {})
            cost = calculate_item_cost(db_item, weight)
            calculated_dough.append({'name': name, 'weight': round(weight, 2), 'pct': pct, 'cost': round(cost, 2)})
            total_dough_weight += weight
    else:
        # Traditional grams entry -> Auto-calculate percentages
        flour_item = next((i for i in dough_items if i.get('is_flour')), dough_items[0] if dough_items else None)
        flour_weight = float(flour_item.get('weight', 1)) if flour_item else 1.0
        
        for item in dough_items:
            name = item.get('name')
            weight = float(item.get('weight', 0))
            pct = (weight / flour_weight * 100.0) if flour_weight > 0 else 0
            db_item = raw_materials_db.get(name, {})
            cost = calculate_item_cost(db_item, weight)
            calculated_dough.append({'name': name, 'weight': weight, 'pct': round(pct, 2), 'cost': round(cost, 2)})
            total_dough_weight += weight

    # Financial Overhead Calculations
    prep_time = float(data.get('prep_time', 0))
    cook_time = float(data.get('cook_time', 0))
    total_labor_min = prep_time + cook_time
    hourly_rate = float(data.get('hourly_rate', 0))
    markup_pct = float(data.get('markup_pct', 0))
    
    labor_cost = (hourly_rate / 60.0) * total_labor_min
    ingredients_cost = sum(i['cost'] for i in calculated_dough)
    
    total_recipe_cost = ingredients_cost + labor_cost
    cost_per_serving = total_recipe_cost / pieces if pieces > 0 else 0
    selling_price = cost_per_serving * (1 + (markup_pct / 100.0))
    
    return jsonify({
        'calculated_dough': calculated_dough,
        'total_dough_weight': round(total_dough_weight, 2),
        'ingredients_cost': round(ingredients_cost, 2),
        'labor_cost': round(labor_cost, 2),
        'total_recipe_cost': round(total_recipe_cost, 2),
        'cost_per_serving': round(cost_per_serving, 2),
        'selling_price': round(selling_price, 2)
    })

if __name__ == '__main__':
    app.run(debug=True)
