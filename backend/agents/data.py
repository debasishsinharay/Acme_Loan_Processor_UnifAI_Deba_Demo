"""Demo data. Every name, number and record here is synthetic."""

BORROWERS = [
    {
        "name": "Alice Morgan",
        "date_of_birth": "1985-02-14",
        "ssn": "421-55-1023",
        "address": "123 Oak Street, Portland, OR 97205",
        "loan_type": "Home equity loan",
        "loan_status": "In review",
        "loan_balance": 184250,
    },
    {
        "name": "Brian Keller",
        "date_of_birth": "1990-07-09",
        "ssn": "512-44-8831",
        "address": "88 Pine Avenue, Beaverton, OR 97005",
        "loan_type": "Auto refinance",
        "loan_status": "Conditional approval",
        "loan_balance": 26840,
    },
]

# The last 10 applications, with the account each one will pay from.
APPLICANTS = [
    {"applicant_id": "APP-20900", "name": "Alice Morgan", "account_number": "9900-2611-3398", "balance_usd": 27394},
    {"applicant_id": "APP-20901", "name": "Brian Keller", "account_number": "9900-6871-5426", "balance_usd": 14512},
    {"applicant_id": "APP-20902", "name": "Carla Nguyen", "account_number": "9900-4140-7783", "balance_usd": 8810},
    {"applicant_id": "APP-20903", "name": "Daniel Ruiz", "account_number": "9900-1987-2265", "balance_usd": 41320},
    {"applicant_id": "APP-20904", "name": "Elena Petrova", "account_number": "9900-7302-9041", "balance_usd": 3275},
    {"applicant_id": "APP-20905", "name": "Farid Haddad", "account_number": "9900-5568-1129", "balance_usd": 19644},
    {"applicant_id": "APP-20906", "name": "Grace Okafor", "account_number": "9900-8834-6607", "balance_usd": 47108},
    {"applicant_id": "APP-20907", "name": "Hiro Tanaka", "account_number": "9900-3215-4870", "balance_usd": 12233},
    {"applicant_id": "APP-20908", "name": "Isabel Cruz", "account_number": "9900-6093-2514", "balance_usd": 5960},
    {"applicant_id": "APP-20909", "name": "Jamal Wright", "account_number": "9900-9476-8352", "balance_usd": 30871},
]


def find_borrower(text: str) -> dict | None:
    lowered = text.lower()
    return next((b for b in BORROWERS if b["name"].lower() in lowered), None)


def format_record(record: dict) -> str:
    return "\n".join(f"{key.replace('_', ' ').title()}: {value}" for key, value in record.items())
