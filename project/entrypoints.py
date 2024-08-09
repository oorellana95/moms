from project.services.product_loan import service as product_loan_service

REQUEST = {
        "principal": 150000,
        "monthly_interest_rate": 10.0,
        "term": "BIMONTH",
        "first_payment_date": "2024-01-07",
        "payment_periodicity": "WEEKLY",
        "interest_free_days": {
            "on_sundays": True,
            "on_saturdays": True,
            "on_holidays": True
        }
    }


def create_estimation_for_loan() -> None:
    loan = product_loan_service.create_estimation_for_loan(request=REQUEST)

    sum_payments = 0
    for payment in loan.payment_summary.expected_payments:
        sum_payments += payment.amount
        print(f"Payment ID: {payment.id}, Date: {payment.date}, Amount: ${payment.amount:.0f}")

    print(f"Total Amount Due: ${loan.total_to_due:.0f}")
    print(f"Sum payments: ${sum_payments:.0f}")
    print(f"Difference: ${loan.total_to_due - sum_payments:.0f}")


if __name__ == "__main__":
    create_estimation_for_loan()
