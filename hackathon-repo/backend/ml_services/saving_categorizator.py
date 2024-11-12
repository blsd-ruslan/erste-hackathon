import pandas as pd
import requests
from pprint import pprint


class UserTransactionAnalyzer:
    def __init__(self, users_file, receipts_file, organizations_file):
        # Load datasets
        self.organizations_df = pd.read_csv(organizations_file)
        self.receipts_df = pd.read_csv(receipts_file)
        self.users_df = pd.read_csv(users_file)

        # Ensure 'create_date' is in datetime format, with error handling
        self.receipts_df['create_date'] = pd.to_datetime(self.receipts_df['create_date'], errors='coerce')

    def get_transactions_for_user(self, user_id: int, year: int = None, month: int = None):
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
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
        }
        payload = {'receiptId': receipt_id}

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            return data.get("receipt", {}).get("items", [])
        else:
            pprint(f"Request failed with status code {response.status_code}")
            return []

    def get_sale_amount_for_receipt(self, receipt_id):
        items = self.get_receipt_items(receipt_id)
        sale_amount = sum(
            item.get('price', 0) * item.get('quantity', 1)
            for item in items if item.get('itemType') == 'Z'
        )
        return sale_amount

    def get_savings_per_category(self, user_transactions, categories):
        sale_amount_per_category = {}

        for category in categories:
            category_transactions = user_transactions[user_transactions['category'] == category]
            total_sale_amount = sum(
                self.get_sale_amount_for_receipt(receipt_id)
                for receipt_id in category_transactions['receipt_id'].unique()
            )
            sale_amount_per_category[category] = total_sale_amount

        return sale_amount_per_category


saving_categorizator = UserTransactionAnalyzer(
    users_file='ml_services/data/Users.csv',
    receipts_file='ml_services/data/Receipts_with_customer_id.csv',
    organizations_file='ml_services/data/Organizations.csv'
)

if __name__ == '__main__':
    # Example usage
    analyzer = UserTransactionAnalyzer(
        users_file='ml_services/data/Users.csv',
        receipts_file='ml_services/data/Receipts_with_customer_id.csv',
        organizations_file='ml_services/data/Organizations.csv'
    )

    # Step 1: Get user transactions and categories
    user_transactions, categories = analyzer.get_transactions_for_user(user_id=2, year=2024, month=10)

    # Step 2: Get the total savings per category
    savings = analyzer.get_savings_per_category(user_transactions, categories)

    # Output the savings per category
    print(savings)
