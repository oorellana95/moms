import datetime

import pydantic

from project.domain.models.products.loan import model as loan_model, payments_resolver as resolver


class CreateNewLoanData(pydantic.BaseModel):
    principal: int
    monthly_interest_rate: float
    term_in_days: int
    first_payment_date: datetime.date
    payment_periodicity_in_days: int


class LoanBuilder:
    def __init__(self, payments_resolver: resolver.LoanPaymentsResolver):
        self.payments_resolver = payments_resolver

    def create_new_loan(self, create_new_loan_data: CreateNewLoanData) -> loan_model.Loan:
        loan = self._create_loan(data=create_new_loan_data)
        self._add_payment_summary(loan=loan)
        return loan

    @staticmethod
    def _create_loan(data: CreateNewLoanData):
        return loan_model.Loan(
            principal=data.principal,
            monthly_interest_rate=data.monthly_interest_rate,
            start_date=data.first_payment_date,
            payment_periodicity_in_days=data.payment_periodicity_in_days,
            term_in_days=data.term_in_days,
            state=loan_model.LoanStates.ACTIVE
        )

    def _add_payment_summary(self, loan: loan_model.Loan):
        loan.payment_summary = loan_model.LoanPaymentSummary(
            interest_free_days=self.payments_resolver.interest_free_days,
            expected_payments=self.payments_resolver.resolve(loan=loan)
        )
