import pandas as pd
import requests
from pprint import pprint
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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
        self.target_month = target_month
        self.user_spending = None

        # self.preprocess_data()
        # self.calculate_user_spending()
        # self.calculate_main_category_statistics()
        # self.calculate_subcategory_statistics()
        # self.calculate_anomalies()

    def preprocess_data(self):
        """
        Preprocesses the raw data, handles missing categories, and filters for the specified month.
        """
        if self.user_id not in self.data['customer_id'].unique():
            raise ValueError(f"User {self.user_id} does not exist in the dataset.")

        # Ensure 'issue_date' is in datetime format
        self.data['issue_date'] = pd.to_datetime(self.data['issue_date'], format='%d.%m.%Y %H:%M:%S', errors='coerce')
        # Filter data up to the target month
        self.data = self.data[self.data['issue_date'].dt.month <= self.target_month]

        # Split the category into primary and subcategory
        self.data[['primary_category', 'subcategory']] = self.data['category_item'].str.split('/', expand=True)

        # Fill missing values and strip whitespace
        self.data['primary_category'] = self.data['primary_category'].fillna("Unknown").str.strip()
        self.data['subcategory'] = self.data['subcategory'].fillna("Unknown").str.strip()

        # Replace empty strings and variations of 'null' with 'Unknown'
        self.data['subcategory'].replace(['', 'null', 'Null', 'NULL'], 'Unknown', inplace=True)

        # Ensure 'receipt_id' is present
        required_columns = ['customer_id', 'issue_date', 'total_price', 'category_item', 'receipt_id']
        missing_columns = set(required_columns) - set(self.data.columns)
        if missing_columns:
            raise ValueError(f"Missing columns in data: {missing_columns}")

    def calculate_user_spending(self):
        """
        Aggregates user spending per category and subcategory.
        """
        user_category_spending = self.data.groupby(['customer_id', 'primary_category', 'subcategory']).agg(
            total_subcat_spent=('total_price', 'sum')
        ).reset_index()

        user_main_category_spending = user_category_spending.groupby(['customer_id', 'primary_category']).agg(
            total_main_spent=('total_subcat_spent', 'sum')
        ).reset_index()

        # Store the results
        self.user_category_spending = user_category_spending
        self.user_main_category_spending = user_main_category_spending

    def calculate_main_category_statistics(self):
        """
        Calculates mean and standard deviation for main categories across all users.
        """
        main_category_stats = self.user_main_category_spending.groupby('primary_category')['total_main_spent'].agg(
            mean_main_spent='mean',
            std_main_spent='std'
        ).reset_index()

        self.user_main_category_spending = self.user_main_category_spending.merge(main_category_stats,
                                                                                  on='primary_category')

        # Calculate z-score for main categories
        self.user_main_category_spending['main_z_score'] = (
                                                                   self.user_main_category_spending[
                                                                       'total_main_spent'] -
                                                                   self.user_main_category_spending['mean_main_spent']
                                                           ) / self.user_main_category_spending['std_main_spent']

    def calculate_subcategory_statistics(self):
        """
        Calculates mean and standard deviation for subcategories and applies z-score calculations.
        """
        category_stats = self.user_category_spending[
            self.user_category_spending['subcategory'] != "Unknown"
            ].groupby(['primary_category', 'subcategory'])['total_subcat_spent'].agg(
            mean_subcat_spent='mean',
            std_subcat_spent='std'
        ).reset_index()

        self.user_category_spending = self.user_category_spending.merge(category_stats,
                                                                        on=['primary_category', 'subcategory'],
                                                                        how='left')

        # Merge main category statistics
        self.user_category_spending = self.user_category_spending.merge(
            self.user_main_category_spending[['customer_id', 'primary_category', 'total_main_spent', 'mean_main_spent',
                                              'std_main_spent', 'main_z_score']],
            on=['customer_id', 'primary_category'], how='left'
        )

        # Calculate z-score for subcategories
        self.user_category_spending['subcat_z_score'] = self.user_category_spending.apply(
            lambda x: (x['total_subcat_spent'] - x['mean_subcat_spent']) / x['std_subcat_spent']
            if x['subcategory'] != "Unknown" and x['std_subcat_spent'] != 0 else None,
            axis=1
        )

    def calculate_anomalies(self):
        """
        Identifies anomalies in spending for the specified user.
        """
        self.user_spending = self.user_category_spending[
            self.user_category_spending['customer_id'] == self.user_id].copy()

        # Determine whether the subcategory z-score is available
        def get_final_z_score(row):
            # Handle cases where subcat_z_score is None or NaN
            if pd.notna(row['subcat_z_score']):
                if abs(row['subcat_z_score']) >= abs(row['main_z_score']):
                    row['final_z_score'] = row['subcat_z_score']
                    row['anomaly_level'] = 'subcategory'
                else:
                    row['final_z_score'] = row['main_z_score']
                    row['anomaly_level'] = 'main_category'
            else:
                row['final_z_score'] = row['main_z_score']
                row['anomaly_level'] = 'main_category'
            return row

        self.user_spending = self.user_spending.apply(get_final_z_score, axis=1)
        self.user_spending['is_anomaly'] = self.user_spending['final_z_score'] > 0.7

    def calculate_total_expenses(self):
        """
        Calculates total expenses for main categories, including all subcategories.
        """
        # Filter data for the specific user
        user_data = self.data[self.data['customer_id'] == self.user_id]

        # Calculate total spending for each main category
        main_category_totals = user_data.groupby('primary_category')['total_price'].sum().reset_index()
        main_category_totals['subcategory'] = ''  # Empty subcategory to differentiate main category totals

        # Calculate total spending for each subcategory without filtering
        subcategory_totals = user_data.groupby(['primary_category', 'subcategory'])['total_price'].sum().reset_index()

        # Combine main category totals with subcategory totals
        combined_totals = pd.concat([main_category_totals, subcategory_totals], ignore_index=True)

        # Sort the combined DataFrame to display main categories first, followed by their subcategories
        combined_totals = combined_totals.sort_values(by=['primary_category', 'subcategory']).reset_index(drop=True)

        # Display the results to the user
        print("Total expenses per main category and subcategory (including all subcategories):")
        print(combined_totals)

        # Store for later use
        self.combined_totals = combined_totals

        return combined_totals

    def get_biggest_anomaly(self):
        """
        Returns the biggest anomaly for the user and computes percentage difference compared to other users.
        """
        anomalies = self.user_spending[self.user_spending['is_anomaly']]
        if not anomalies.empty:
            biggest_anomaly = anomalies.sort_values(by='final_z_score', key=abs, ascending=False).head(1)
            # Get category, subcategory, and anomaly level
            primary_category = biggest_anomaly['primary_category'].iloc[0]
            subcategory = biggest_anomaly['subcategory'].iloc[0]
            anomaly_level = biggest_anomaly['anomaly_level'].iloc[0]

            other_users_data = self.data[self.data['customer_id'] != self.user_id]

            if anomaly_level == 'subcategory' and subcategory != "Unknown" and pd.notna(subcategory):
                # Compute total spend per user in this subcategory
                other_users_spend = other_users_data[
                    (other_users_data['primary_category'] == primary_category) &
                    (other_users_data['subcategory'] == subcategory)
                    ].groupby('customer_id')['total_price'].sum()
                # Compute average spend
                avg_other_users_spend = other_users_spend.mean()
                # Get user's spend in this subcategory
                user_spend = biggest_anomaly['total_subcat_spent'].iloc[0]
            else:
                # Compute total spend per user in this main category
                other_users_spend = other_users_data[
                    other_users_data['primary_category'] == primary_category
                    ].groupby('customer_id')['total_price'].sum()
                # Compute average spend
                avg_other_users_spend = other_users_spend.mean()
                # Get user's spend in this main category
                user_spend = biggest_anomaly['total_main_spent'].iloc[0]

            if avg_other_users_spend != 0 and not pd.isna(avg_other_users_spend):
                # Compute percentage difference
                percent_difference = ((user_spend - avg_other_users_spend) / avg_other_users_spend) * 100
            else:
                percent_difference = None

            # Add the computed values to the DataFrame
            biggest_anomaly['avg_other_users_spend'] = avg_other_users_spend
            biggest_anomaly['percent_difference'] = percent_difference

            if anomaly_level == 'subcategory':
                message = (f"Hi! In this month you spent {percent_difference:.2f}% more than other users in the "
                           f"{biggest_anomaly['subcategory'].values[0]} category.")
            else:
                message = (f"Hi! In this month you spent {percent_difference:.2f}% more than other users in the "
                           f"{biggest_anomaly['primary_category'].values[0]} category.")

            biggest_anomaly['message'] = message  # Add message as a new column

            # Save to CSV
            biggest_anomaly.to_csv(f'ml_services/output/user_{self.user_id}_biggest_anomaly.csv', index=False)

            return biggest_anomaly[[
                'customer_id', 'primary_category', 'subcategory', 'total_subcat_spent',
                'total_main_spent', 'mean_subcat_spent', 'std_subcat_spent',
                'mean_main_spent', 'std_main_spent', 'main_z_score', 'subcat_z_score',
                'final_z_score', 'anomaly_level', 'is_anomaly', 'avg_other_users_spend',
                'percent_difference', 'message'
            ]]
        else:
            print(f"No anomalies found for User {self.user_id} in October.")
            return None

    def identify_anomalous_products(self):
        """
        Identifies products contributing to the spending anomalies.
        """
        anomalies = self.user_spending[self.user_spending['is_anomaly']]
        if anomalies.empty:
            print(f"No anomalies found for User {self.user_id} in October.")
            return None

        # Get anomalous categories and subcategories
        anomalous_categories = anomalies[['primary_category', 'subcategory']]

        # Filter transactions in the anomalous categories for the target month
        anomalous_transactions = self.data[
            (self.data['customer_id'] == self.user_id) &
            (self.data['primary_category'].isin(anomalous_categories['primary_category'])) &
            (self.data['subcategory'].isin(anomalous_categories['subcategory'])) &
            (self.data['issue_date'].dt.month == self.target_month)
            ]

        # Get receipt IDs from anomalous transactions
        receipt_ids = anomalous_transactions['receipt_id'].unique()

        if len(receipt_ids) == 0:
            print("No receipt IDs found for anomalous transactions.")
            return None

        # Initialize UserTransactionAnalyzer
        uta = UserTransactionAnalyzer(
            users_file='ml_services/data/Users.csv',
            receipts_file='ml_services/data/Receipts_with_customer_id.csv',
            organizations_file='ml_services/data/Organizations.csv'
        )

        # Get product-level data for the receipts
        product_spending_list = []

        for receipt_id in receipt_ids:
            items = uta.get_receipt_items(receipt_id)
            if not items:
                continue
            for item in items:
                product_name = item.get('name', 'Unknown')
                price = item.get('price', 0)
                quantity = item.get('quantity', 1)
                total_price = price * quantity
                product_spending_list.append({
                    'product_name': product_name,
                    'price': price,
                    'quantity': quantity,
                    'total_price': total_price,
                    'receipt_id': receipt_id
                })

        # Convert to DataFrame
        product_spending_df = pd.DataFrame(product_spending_list)

        if product_spending_df.empty:
            print("No product-level data available for the anomalous transactions.")
            return None

        # Aggregate spending by product
        product_spending = product_spending_df.groupby('product_name').agg(
            total_spent=('total_price', 'sum'),
            quantity=('quantity', 'sum')
        ).reset_index()

        # Sort products by total spent
        product_spending = product_spending.sort_values(by='total_spent', ascending=False)

        # Save to CSV
        product_spending.to_csv(f'ml_services/output/user_{self.user_id}_anomalous_products.csv', index=False)

        return product_spending

    def analyze_anomalies(self):
        """
        Performs full analysis to identify the biggest product causing anomalies.
        """
        anomalies = self.get_biggest_anomaly()
        if anomalies is not None:
            product_spending = self.identify_anomalous_products()

            if product_spending is not None and not product_spending.empty:
                # Identify the product contributing most to the anomaly
                top_product = product_spending.iloc[0]  # Get the top product
                print("Product contributing most to the spending anomaly:")
                print(top_product.to_frame().T)
                # Save top product to CSV
                top_product.to_frame().T.to_csv(f'ml_services/output/user_{self.user_id}_top_product_anomaly.csv', index=False)
            else:
                print("No product-level data available for the anomalous transactions.")
        else:
            print("No anomalies detected.")

    def save_all_data_to_csv(self):
        """
        Saves all relevant data to CSV files after analysis.
        """
        # Ensure the output directory exists
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)

        # Save total expenses
        if not hasattr(self, 'combined_totals'):
            self.calculate_total_expenses()
        self.combined_totals.to_csv(f'ml_services/{output_dir}/user_{self.user_id}_total_expenses.csv', index=False)

        # Save user category spending
        self.user_category_spending.to_csv(f'ml_services/{output_dir}/user_{self.user_id}_category_spending.csv', index=False)

        # Save user main category spending
        self.user_main_category_spending.to_csv(f'ml_services/{output_dir}/user_{self.user_id}_main_category_spending.csv',
                                                index=False)

        # Save main category statistics
        main_category_stats = self.user_main_category_spending.groupby('primary_category')['total_main_spent'].agg(
            mean_main_spent='mean',
            std_main_spent='std'
        ).reset_index()
        main_category_stats.to_csv(f'ml_services/{output_dir}/user_{self.user_id}_main_category_stats.csv', index=False)

        # Save subcategory statistics
        category_stats = self.user_category_spending.groupby(
            ['primary_category', 'subcategory']
        )['total_subcat_spent'].agg(
            mean_subcat_spent='mean',
            std_subcat_spent='std'
        ).reset_index()
        category_stats.to_csv(f'ml_services/{output_dir}/user_{self.user_id}_subcategory_stats.csv', index=False)

        # Save user spending with anomalies
        self.user_spending.to_csv(f'ml_services/{output_dir}/user_{self.user_id}_spending_with_anomalies.csv', index=False)

        print(f"All data saved to '{output_dir}' directory.")


analyzer = SpendingAnalyzer(file_path='ml_services/data/Merged_Spending_Data.csv', user_id=1)

if __name__ == '__main__':
    # Example usage
    analyzer = SpendingAnalyzer(file_path='ml_services/data/Merged_Spending_Data.csv', user_id=1)
    analyzer.analyze_anomalies()
    analyzer.save_all_data_to_csv()
