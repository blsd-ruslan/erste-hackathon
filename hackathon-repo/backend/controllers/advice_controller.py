import os

import pandas as pd
from fastapi import APIRouter
from ml_services.anomaly_detector import analyzer
from ml_services.saving_categorizator import saving_categorizator
advice_router = APIRouter()

@advice_router.get("/advices")
def get_advice(user_id: int = 12):
    analyzer.user_id = user_id
    analyzer.preprocess_data()
    analyzer.calculate_user_spending()
    analyzer.calculate_main_category_statistics()
    analyzer.calculate_subcategory_statistics()
    analyzer.calculate_anomalies()
    analyzer.analyze_anomalies()
    analyzer.save_all_data_to_csv()
    output_file_path = f'ml_services/output/user_{user_id}_biggest_anomaly.csv'

    if os.path.exists(output_file_path):
        anomaly_df = pd.read_csv(output_file_path)
        if not anomaly_df.empty:
            message = anomaly_df['message'].iloc[0]
            return {"user_id": user_id, "advice_message": message}
        else:
            return {"user_id": user_id, "message": "No anomalies found in the specified period."}


@advice_router.get("/get_anomaly_product")
def get_anomaly_product(user_id: int = 12):
    # Set the analyzer's user_id
    analyzer.user_id = user_id
    output_file_path = f'ml_services/output/user_{user_id}_top_product_anomaly.csv'

    # Check if the file exists
    if os.path.exists(output_file_path):
        product_df = pd.read_csv(output_file_path)
        if not product_df.empty:
            product = product_df['product_name'].iloc[0]
            return {"user_id": user_id, "advice_message": f"Top anomaly product: {product}"}
        else:
            return {"user_id": user_id, "message": "No anomalies found in the specified period."}


@advice_router.get("/get_expense_categories")
def get_expense_categories(user_id: int = 12):
    # Set the analyzer's user_id
    analyzer.user_id = user_id
    output_file_path = f'ml_services/output/user_{user_id}_total_expenses.csv'

    # Check if the file exists
    if os.path.exists(output_file_path):
        total_expenses_df = pd.read_csv(output_file_path)

        if not total_expenses_df.empty:
            # Replace NaN and infinite values with a default (like 0 or empty string)
            total_expenses_df = total_expenses_df.replace([float('inf'), -float('inf')], 0)
            total_expenses_df = total_expenses_df.fillna(0)

            # Convert the DataFrame to a list of dictionaries
            expenses_list = total_expenses_df.to_dict(orient="records")
            return {"user_id": user_id, "expense_categories": expenses_list}
        else:
            return {"user_id": user_id, "message": "No expenses found in the specified period."}

@advice_router.get("/get_discounted_categories")
def get_discounted_categories(user_id: int = 2):
    # Set the analyzer's user_id
    user_transactions, categories = saving_categorizator.get_transactions_for_user(user_id=user_id, year=2024, month=10)

    savings = saving_categorizator.get_savings_per_category(user_transactions, categories)
    return {"user_id": user_id, "discounted_categories": savings}