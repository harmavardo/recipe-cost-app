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

def calculate_unit_cost(item):
    purchase_cost = float(item.get('purchase_cost', 0))
    purchase_qty = float(item.get('purchase_quantity', 1))
    return purchase_cost / purchase_qty if purchase_qty > 0 else 0.0

@app.route('/')
def home():
    db = load_db()
    return render_template('index.html', db=db)

@app.route('/ingredients_page')
def ingredients_page():
    db = load_db()
    return render_template('ingredients.html', db=db)

@app.route('/api/db', methods=['GET', 'POST'])
def api_db():
    if request.method == 'POST':
        data = request.json
        save_db(data)
        return jsonify({"status": "success"})
    return jsonify(load_db())

@app.route('/calculate', methods=['POST'])
def calculate():
    db = load_db()
    data = request.json
    
    # Create price mapping dicts
    ing_prices = {i['name']: calculate_unit_cost(i) for i in db.get('ingredients', [])}
    pkg_prices = {i['name']: calculate_unit_cost(i) for i in db.get('packaging', [])}
    oth_prices = {i['name']: calculate_unit_cost(i) for i in db.get('other', [])}
    
    # 1. Formula Panadera Sections Processing
    formula_sections = data.get('sections', [])
    processed_sections = []
    
    for sec in formula_sections:
        pieces = float(sec.get('pieces', 0))
        grams_per_piece = float(sec.get('grams_per_piece', 0))
        target_dough = pieces * grams_per_piece
        
        items = sec.get('items', [])
        total_pct = sum(float(it.get('pct', 0)) for it in items)
        flour_weight = (target_dough / total_pct * 100) if total_pct > 0 else 0
        
        processed_items = []
        sec_total_weight = 0.0
        sec_total_cost = 0.0
        
        for it in items:
            name = it.get('name')
            pct = float(it.get('pct', 0))
            weight = round((flour_weight * pct / 100.0), 2)
            unit_cost = ing_prices.get(name, 0.0)
            cost = round(weight * unit_cost, 2)
            
            sec_total_weight += weight
            sec_total_cost += cost
            processed_items.append({
                'name': name,
                'weight': weight,
                'pct': pct,
                'unit_cost': round(unit_cost, 4),
                'cost': cost
            })
            
        processed_sections.append({
            'name': sec.get('name', 'Component'),
            'pieces': pieces,
            'grams_per_piece': grams_per_piece,
            'total_dough': round(sec_total_weight, 2),
            'items': processed_items,
            'total_cost': round(sec_total_cost, 2)
        })
        
    # 2. Recipe Calculator Items Processing
    calc_ingredients = data.get('calc_ingredients', [])
    calc_packaging = data.get('calc_packaging', [])
    calc_other = data.get('calc_other', [])
    
    def process_cost_list(items, price_dict):
        res = []
        total = 0.0
        for it in items:
            name = it.get('name')
            qty = float(it.get('qty', 0))
            unit_cost = price_dict.get(name, 0.0)
            cost = qty * unit_cost
            total += cost
            res.append({'name': name, 'qty': qty, 'unit_cost': round(unit_cost, 4), 'cost': round(cost, 2)})
        return res, round(total, 2)

    proc_ing, total_ing_cost = process_cost_list(calc_ingredients, ing_prices)
    proc_pkg, total_pkg_cost = process_cost_list(calc_packaging, pkg_prices)
    proc_oth, total_oth_cost = process_cost_list(calc_other, oth_prices)
    
    # 3. Overhead & Pricing
    batch_size = float(data.get('batch_size', 1))
    prep_min = float(data.get('prep_time', 0))
    cook_min = float(data.get('cook_time', 0))
    total_labor_min = prep_min + cook_min
    hourly_rate = float(data.get('hourly_rate', 0))
    markup_pct = float(data.get('markup_pct', 0))
    
    labor_cost = (hourly_rate / 60.0) * total_labor_min
    total_material_cost = total_ing_cost + total_pkg_cost + total_oth_cost
    total_recipe_cost = total_material_cost + labor_cost
    cost_per_serving = total_recipe_cost / batch_size if batch_size > 0 else 0
    selling_price = cost_per_serving * (1 + (markup_pct / 100.0))
    
    return jsonify({
        'formula_sections': processed_sections,
        'calc_ingredients': proc_ing,
        'calc_packaging': proc_pkg,
        'calc_other': proc_oth,
        'total_ingredients_cost': total_ing_cost,
        'total_packaging_cost': total_pkg_cost,
        'total_other_cost': total_oth_cost,
        'labor_cost': round(labor_cost, 2),
        'total_recipe_cost': round(total_recipe_cost, 2),
        'cost_per_serving': round(cost_per_serving, 2),
        'selling_price': round(selling_price, 2)
    })

if __name__ == '__main__':
    app.run(debug=True)
