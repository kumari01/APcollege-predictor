from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load and clean data once at startup
df = pd.read_excel("data/cutoff_data.xlsx")
rank_cols = [col for col in df.columns if 'BOYS' in col or 'GIRLS' in col]
df[rank_cols] = df[rank_cols].apply(pd.to_numeric, errors='coerce')
df.dropna(subset=['NAME OF THE INSTITUTION'], inplace=True)
df.reset_index(drop=True, inplace=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        rank = int(request.form.get('rank', 0)) + 3  # buffer +3
    except ValueError:
        return jsonify({"error": "Invalid rank."})

    category = request.form.get('category', '').upper()
    gender = request.form.get('gender', '').upper()
    branch = request.form.get('branch', '').upper()
    instcode = request.form.get('instcode', '').upper()
    district = request.form.get('district', '').upper()

    col_name = f"{category}_{gender}"

    if col_name not in df.columns:
        return jsonify([])  # no such category_gender combo

    # Apply filters
    filtered_df = df.copy()
    if branch:
        filtered_df = filtered_df[filtered_df['branch_code'] == branch]
    if instcode:
        if instcode not in df['INSTCODE'].unique():
            return jsonify({"error": f"Invalid College Code: {instcode}"})
        else:
            filtered_df = filtered_df[filtered_df['INSTCODE'] == instcode]

    if district:
        if district not in df['DIST'].unique():
            return jsonify({"error": f"Invalid District Code: {district}"})
        else:
            filtered_df = filtered_df[filtered_df['DIST'] == district]


    # Filter by rank eligibility
    filtered_df = filtered_df[filtered_df[col_name] >= rank]

    # Prepare final data
    result = filtered_df[[
        "NAME OF THE INSTITUTION", "branch_code", "PLACE", "DIST", col_name
    ]].rename(columns={col_name: "Cutoff Rank"})

    return result.to_dict(orient='records')

if __name__ == '__main__':
    app.run(debug=True)
