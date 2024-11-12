import pandas as pd
import requests


class IntegratedSpendingAnalyzer:
    def __init__(self, users_file, receipts_file, organizations_file, user_id, target_month=None):
        # Load datasets
        self.organizations_df = pd.read_csv(organizations_file)
        self.receipts_df = pd.read_csv(receipts_file)
        self.users_df = pd.read_csv(users_file)

        # Parameters
        self.user_id = user_id
        self.target_month = target_month

        # Ensure 'create_date' is in datetime format, with error handling
        self.receipts_df['create_date'] = pd.to_datetime(self.receipts_df['create_date'], errors='coerce')

        # Processed data for further use
        self.user_spending = None
        self.anomaly_data = None

        self.preprocess_data()

    def preprocess_data(self):
        """Filter for target user and optionally by month, split categories."""
        if self.user_id not in self.receipts_df['customer_id'].unique():
            raise ValueError(f"User {self.user_id} does not exist in the dataset.")

        # Filter by user and optionally by month if specified
        self.receipts_df = self.receipts_df[self.receipts_df['customer_id'] == self.user_id]
        if self.target_month:
            self.receipts_df = self.receipts_df[self.receipts_df['create_date'].dt.month == self.target_month]

        # Split the category into primary and subcategory, handle missing values
        self.receipts_df[['primary_category', 'subcategory']] = self.receipts_df['category'].str.split('/', expand=True)
        self.receipts_df['primary_category'].fillna("Unknown", inplace=True)
        self.receipts_df['subcategory'].fillna("Unknown", inplace=True)

    def calculate_user_spending(self):
        """Aggregates user spending per category and subcategory."""
        self.user_spending = self.receipts_df.groupby(['primary_category', 'subcategory']).agg(
            total_spent=('total_price', 'sum')
        ).reset_index()

    @staticmethod
    def get_receipt_items(receipt_id):
        """Fetches receipt data from the API using the provided receipt ID and returns the receipt items."""
        url = 'https://ekasa.financnasprava.sk/mdu/api/v1/opd/receipt/find'
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json;charset=UTF-8',
            'User-Agent': 'Mozilla/5.0'
        }
        payload = {'receiptId': receipt_id}

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            return data.get("receipt", {}).get("items", [])
        else:
            print(f"Request failed with status code {response.status_code}")
            return []

    def calculate_main_category_statistics(self):
        """Calculates mean and standard deviation for main categories across all months for this user."""
        category_stats = self.user_spending.groupby('primary_category')['total_spent'].agg(
            mean_spent='mean',
            std_spent='std'
        ).reset_index()

        self.user_spending = self.user_spending.merge(category_stats, on='primary_category')

        # Calculate z-score
        self.user_spending['z_score'] = (self.user_spending['total_spent'] - self.user_spending['mean_spent']) / \
                                        self.user_spending['std_spent']

    def detect_anomalies(self):
        """Identifies anomalies in user spending across all months for flagged categories."""
        self.user_spending['is_anomaly'] = self.user_spending['z_score'].abs() > 1.5  # Threshold for anomaly

        # Store anomalies separately for further analysis
        self.anomaly_data = self.user_spending[self.user_spending['is_anomaly']]

    def analyze_anomaly(self):
        """Analyzes the details of the largest anomaly by checking historical receipts for expensive items."""
        if self.anomaly_data.empty:
            print("No anomalies detected.")
            return None

        # Sort anomalies by z-score to get the largest one
        largest_anomaly = self.anomaly_data.iloc[self.anomaly_data['z_score'].abs().idxmax()]

        category_anomalous = largest_anomaly['primary_category']

        # Check receipts in the anomalous category across all months
        receipts_in_category = self.receipts_df[self.receipts_df['primary_category'] == category_anomalous][
            'receipt_id'].unique()

        # Analyze expensive items in anomalous receipts
        expensive_items = []
        for receipt_id in receipts_in_category:
            items = self.get_receipt_items(receipt_id)
            for item in items:
                if item.get('itemType') == 'Z':  # Only consider sale items
                    item_total_cost = item.get('price', 0) * item.get('quantity', 1)
                    expensive_items.append(
                        {
                            "name": item.get('name', 'Unknown'),
                            "unit_price": item.get('price', 0),
                            "quantity": item.get('quantity', 1),
                            "total_cost": item_total_cost
                        }
                    )

        # Sort by total cost and filter out items above a certain threshold
        expensive_items.sort(key=lambda x: x["total_cost"], reverse=True)
        significant_items = [item for item in expensive_items if item["total_cost"] > 50]  # Threshold example

        return {
            "category": category_anomalous,
            "largest_anomaly_details": largest_anomaly,
            "expensive_items": significant_items[:5]  # Show top 5 most expensive items in the anomaly
        }


# Example usage
analyzer = IntegratedSpendingAnalyzer(
    users_file='data/Users.csv',
    receipts_file='data/Receipts_with_customer_id.csv',
    organizations_file='data/Organizations.csv',
    user_id=2
)

analyzer.calculate_user_spending()
analyzer.calculate_main_category_statistics()
analyzer.detect_anomalies()
anomaly_analysis = analyzer.analyze_anomaly()

print(anomaly_analysis)
