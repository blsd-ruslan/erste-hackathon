import pandas as pd
import requests
from pprint import pprint
import os


class UserTransactionAnalyzer:
    def __init__(self, users_file, receipts_file, organizations_file):
        # Load datasets
        self.organizations_df = pd.read_csv(organizations_file)
        self.receipts_df = pd.read_csv(receipts_file)
        self.users_df = pd.read_csv(users_file)

        # Ensure 'create_date' is in datetime format, with error handling
        self.receipts_df['create_date'] = pd.to_datetime(self.receipts_df['create_date'], errors='coerce')

    def get_transactions_for_user(self, user_id: int, year: int = None, month: int = None):
        """
        Retrieves transactions for a specific user, optionally filtered by year and month.
        """
        # Filter by user_id
        user_transactions = self.receipts_df[self.receipts_df['customer_id'] == user_id]

        # Filter by year and month if specified
        if year:
            user_transactions = user_transactions[user_transactions['create_date'].dt.year == year]
        if month:
            user_transactions = user_transactions[user_transactions['create_date'].dt.month == month]

        # Filter out transactions with empty categories
        user_transactions = user_transactions[user_transactions['category'].notna()]

        # Get unique categories
        categories = user_transactions['category'].unique()

        return user_transactions, categories

    @staticmethod
    def get_receipt_items(receipt_id):
        """
        Fetches receipt data from the API using the provided receipt ID and returns the receipt items.
        """
        url = 'https://ekasa.financnasprava.sk/mdu/api/v1/opd/receipt/find'
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json;charset=UTF-8',
            'User-Agent': 'Mozilla/5.0'
        }
        payload = {'receiptId': receipt_id}

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("receipt", {}).get("items", [])
        except requests.exceptions.RequestException as e:
            pprint(f"An error occurred while fetching receipt items: {e}")
            return []

    def get_sale_amount_for_receipt(self, receipt_id):
        """
        Calculates the total sale amount for a given receipt ID by summing up the price of items.
        """
        items = self.get_receipt_items(receipt_id)
        sale_amount = sum(
            item.get('price', 0) * item.get('quantity', 1)
            for item in items if item.get('itemType') == 'Z'
        )
        return sale_amount

    def get_savings_per_category(self, user_transactions, categories):
        """
        Calculates the total savings per category for a user's transactions.
        """
        sale_amount_per_category = {}

        for category in categories:
            category_transactions = user_transactions[user_transactions['category'] == category]
            total_sale_amount = sum(
                self.get_sale_amount_for_receipt(receipt_id)
                for receipt_id in category_transactions['receipt_id'].unique()
            )
            sale_amount_per_category[category] = total_sale_amount

        return sale_amount_per_category


class SpendingAnalyzer:
    def __init__(self, file_path, user_id, target_month=10):
        self.data = pd.read_csv(file_path)
        self.user_id = user_id
        self.target_month = target_month  # October
        self.user_spending = None

        self.preprocess_data()
        self.calculate_historical_behavior()
        self.identify_october_anomalies()
        self.analyze_and_report_anomalies()

    def preprocess_data(self):
        """
        Preprocesses the raw data, handles missing categories, and separates historical and October data.
        """
        if self.user_id not in self.data['customer_id'].unique():
            raise ValueError(f"User {self.user_id} does not exist in the dataset.")

        # Ensure 'issue_date' is in datetime format
        self.data['issue_date'] = pd.to_datetime(self.data['issue_date'], format='%d.%m.%Y %H:%M:%S', errors='coerce')

        # Split the category into primary and subcategory
        self.data[['primary_category', 'subcategory']] = self.data['category_item'].str.split('/', expand=True, n=1)

        # Fill missing values and strip whitespace
        self.data['primary_category'] = self.data['primary_category'].fillna("Unknown").str.strip()
        self.data['subcategory'] = self.data['subcategory'].fillna("Unknown").str.strip()

        # Replace empty strings and variations of 'null' with 'Unknown'
        self.data['subcategory'].replace(['', 'null', 'Null', 'NULL'], 'Unknown', inplace=True)

        # Ensure 'receipt_id' is present
        required_columns = ['customer_id', 'issue_date', 'total_price', 'category_item', 'receipt_id', 'quantity',
                            'product_name']
        missing_columns = set(required_columns) - set(self.data.columns)
        if missing_columns:
            raise ValueError(f"Missing columns in data: {missing_columns}")

        # Separate historical data (before October) and October data
        self.historical_data = self.data[self.data['issue_date'].dt.month < self.target_month]
        self.october_data = self.data[self.data['issue_date'].dt.month == self.target_month]

        # Ensure we have data for the user in historical data
        if self.historical_data[self.historical_data['customer_id'] == self.user_id].empty:
            raise ValueError(f"No historical data available for User {self.user_id} before October.")

    def calculate_historical_behavior(self):
        """
        Calculates the user's historical purchasing behavior for each product.
        """
        user_historical = self.historical_data[self.historical_data['customer_id'] == self.user_id]

        # Aggregate historical purchase amounts for each product
        self.user_historical_product_stats = user_historical.groupby('product_name').agg(
            historical_avg_quantity=('quantity', 'mean'),
            historical_std_quantity=('quantity', 'std'),
            historical_max_quantity=('quantity', 'max')
        ).reset_index()

    def identify_october_anomalies(self):
        """
        Identifies anomalies in the user's October purchases by comparing to historical behavior.
        """
        user_october = self.october_data[self.october_data['customer_id'] == self.user_id]

        if user_october.empty:
            print(f"No purchase data for User {self.user_id} in October.")
            return

        # Merge October data with historical stats
        self.user_october_purchases = user_october.merge(
            self.user_historical_product_stats,
            on='product_name',
            how='left'
        )

        # Fill NaN values for products not seen before
        self.user_october_purchases['historical_avg_quantity'].fillna(0, inplace=True)
        self.user_october_purchases['historical_std_quantity'].fillna(0, inplace=True)
        self.user_october_purchases['historical_max_quantity'].fillna(0, inplace=True)

        # Calculate z-score for quantity
        def calculate_z_score(row):
            if row['historical_std_quantity'] > 0:
                return (row['quantity'] - row['historical_avg_quantity']) / row['historical_std_quantity']
            else:
                # If std is 0, but quantity differs from historical average, flag as anomaly
                if row['quantity'] != row['historical_avg_quantity']:
                    return float('inf')  # Infinite z-score
                else:
                    return 0

        self.user_october_purchases['quantity_z_score'] = self.user_october_purchases.apply(calculate_z_score, axis=1)

        # Identify anomalies based on z-score threshold
        z_score_threshold = 2  # You can adjust this threshold
        self.user_october_purchases['is_anomaly'] = self.user_october_purchases[
                                                        'quantity_z_score'].abs() > z_score_threshold

        # For products not seen before, we can also flag them as potential anomalies
        self.user_october_purchases['is_new_product'] = self.user_october_purchases['historical_avg_quantity'] == 0

    def analyze_and_report_anomalies(self):
        """
        Analyzes anomalies and prepares a report.
        """
        anomalies = self.user_october_purchases[
            self.user_october_purchases['is_anomaly'] | self.user_october_purchases['is_new_product']]

        if anomalies.empty:
            print(f"No anomalies detected for User {self.user_id} in October based on historical data.")
            return None

        # Prepare a report
        anomalies_report = anomalies[[
            'product_name', 'quantity', 'historical_avg_quantity', 'historical_std_quantity',
            'quantity_z_score', 'is_anomaly', 'is_new_product', 'receipt_id', 'issue_date',
            'primary_category', 'subcategory', 'total_price'
        ]]

        # Save to CSV
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        anomalies_report.to_csv(f'{output_dir}/user_{self.user_id}_october_anomalies.csv', index=False)

        print("Anomalies detected in October purchases:")
        print(anomalies_report)

        return anomalies_report

    def save_all_data_to_csv(self):
        """
        Saves all relevant data to CSV files after analysis.
        """
        # Ensure the output directory exists
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)

        # Save historical behavior
        self.user_historical_product_stats.to_csv(f'{output_dir}/user_{self.user_id}_historical_behavior.csv',
                                                  index=False)

        # Save October purchases
        self.user_october_purchases.to_csv(f'{output_dir}/user_{self.user_id}_october_purchases.csv', index=False)

        print(f"All data saved to '{output_dir}' directory.")

    def analyze_anomalies(self):
        """
        Analyzes the anomalies to identify the most significant ones and provide recommendations.
        """
        anomalies_report = self.analyze_and_report_anomalies()
        if anomalies_report is not None:
            # Sort anomalies by the absolute value of the z-score
            anomalies_report['abs_z_score'] = anomalies_report['quantity_z_score'].abs()
            anomalies_report = anomalies_report.sort_values(by='abs_z_score', ascending=False)

            # Identify the top N anomalies (e.g., top 5)
            top_anomalies = anomalies_report.head(5)

            # Generate recommendations or messages
            recommendations = []
            for index, row in top_anomalies.iterrows():
                product_name = row['product_name']
                quantity = row['quantity']
                historical_avg = row['historical_avg_quantity']
                z_score = row['quantity_z_score']
                is_new_product = row['is_new_product']
                issue_date = row['issue_date']

                if is_new_product:
                    message = (f"On {issue_date.date()}, you purchased '{product_name}' for the first time. "
                               f"Consider if this purchase aligns with your usual spending habits.")
                else:
                    message = (f"On {issue_date.date()}, you purchased '{product_name}' in a quantity ({quantity}) "
                               f"significantly different from your historical average ({historical_avg:.2f}).")

                recommendations.append({
                    'product_name': product_name,
                    'quantity': quantity,
                    'historical_avg_quantity': historical_avg,
                    'quantity_z_score': z_score,
                    'message': message
                })

            # Convert recommendations to DataFrame
            recommendations_df = pd.DataFrame(recommendations)

            # Save recommendations to CSV
            output_dir = 'output'
            os.makedirs(output_dir, exist_ok=True)
            recommendations_df.to_csv(f'{output_dir}/user_{self.user_id}_anomaly_recommendations.csv', index=False)

            # Print the recommendations
            print("Top Anomaly Recommendations:")
            print(recommendations_df[
                      ['product_name', 'quantity', 'historical_avg_quantity', 'quantity_z_score', 'message']])

            return recommendations_df
        else:
            print("No anomalies to analyze.")
            return None


if __name__ == '__main__':
    # Example usage
    analyzer = SpendingAnalyzer(file_path='data/Merged_Spending_Data.csv', user_id=1)
    analyzer.save_all_data_to_csv()
