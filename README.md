# ship-pilot

A toy repo for testing a GitHub review gate. It holds synthetic data only: no app code, no customer data and no credentials.

`receipt_check` classifies synthetic review receipts (SHIP / BLOCK / NO_VOTE). A change is eligible to merge only with two SHIP receipts from different non-author model families at the exact full 40-character head SHA, and no BLOCK.

Run the tests: `python -m unittest discover -s tests -v`
