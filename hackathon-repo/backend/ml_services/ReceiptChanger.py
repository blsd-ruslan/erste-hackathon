import pandas as pd
import numpy as np

# Load the Receipts data
receipts_df = pd.read_csv('data/Receipts.csv')

# Generate random user IDs between 1 and 42 for each row in Receipts
np.random.seed(0)  # Optional: for reproducibility of results
receipts_df['customer_id'] = np.random.randint(1, 43, size=len(receipts_df))

# Save the modified Receipts DataFrame to a new file, or overwrite if desired
receipts_df.to_csv('data/Receipts_with_customer_id.csv', index=False)

# Display the first few rows to verify the changes
print("Modified Receipts Data with Random Customer IDs:")
print(receipts_df.head())