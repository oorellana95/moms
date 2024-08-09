import datetime
from typing import Tuple, Optional, List

import pydantic

from project.commons import holidays
from project.domain.models.products.loan import model as loan_model


class ResolverSettings(pydantic.BaseModel):
    interest_free_days: loan_model.InterestFreeDays
    applied_holidays: List[holidays.Holiday] = []
    rounding_base: int = 500


class LoanPaymentsResolver:
    def __init__(self, settings: ResolverSettings):
        self.interest_free_days = settings.interest_free_days
        self.applied_holidays = settings.applied_holidays
        self.rounding_base = settings.rounding_base

    def resolve(self, loan: loan_model.Loan) -> List[loan_model.LoanPayment]:
        effective_payments = self._get_effective_payments(loan=loan)
        quote, last_quote = self._calculate_quote_amounts(loan=loan, effective_payments=effective_payments)
        return self._generate_payments(loan=loan, quote=quote, last_quote=last_quote, effective_payments=effective_payments)

    def _get_effective_payments(self, loan: loan_model.Loan) -> int:
        if loan.payment_periodicity_in_days == 1:
            special_days_count = self._count_special_days_in_period(
                start_date=loan.start_date,
                payment_periodicity=loan.payment_periodicity_in_days,
                term_in_days=loan.term_in_days
            )
            return loan.number_of_payments - special_days_count

        return loan.number_of_payments

    def _calculate_quote_amounts(self, loan: loan_model.Loan, effective_payments: int) -> Tuple[float, Optional[float]]:
        exact_quote = loan.total_to_due / effective_payments
        rounded_quote = self.rounding_base * round(exact_quote / self.rounding_base)
        last_quote = loan.total_to_due - rounded_quote * (effective_payments - 1)
        return rounded_quote, last_quote

    def _generate_payments(self, loan: loan_model.Loan, quote: float, last_quote: Optional[float],
                           effective_payments: int) -> List[loan_model.LoanPayment]:
        payments = []
        payment_date = loan.start_date

        for payment_count in range(1, effective_payments + 1):
            while not self._is_payment_date_valid(payment_date):
                payment_date += datetime.timedelta(days=1)

            if payment_count < effective_payments or (payment_count == effective_payments and last_quote is not None):
                payment_quote = last_quote if payment_count == effective_payments else quote
                payments.append(
                    self._create_payment(payment_id=payment_count, payment_date=payment_date, quote=payment_quote))

            payment_date += datetime.timedelta(days=loan.payment_periodicity_in_days)

        return payments

    def _create_payment(self, payment_id: int, payment_date: datetime.date, quote: float) -> loan_model.LoanPayment:
        return loan_model.LoanPayment(id=payment_id, date=payment_date, amount=quote)

    def _count_special_days_in_period(self, start_date: datetime.date, payment_periodicity: int,
                                      term_in_days: int) -> int:
        count = 0
        current_date = start_date

        while (current_date - start_date).days <= term_in_days:
            if not self._is_payment_date_valid(current_date):
                count += 1
            current_date += datetime.timedelta(days=payment_periodicity)

        return count

    def _is_payment_date_valid(self, date: datetime.date) -> bool:
        if self.interest_free_days.on_sundays and date.weekday() == 6:  # 6 corresponds to Sunday
            return False
        if self.interest_free_days.on_saturdays and date.weekday() == 5:  # 5 corresponds to Saturday
            return False
        if self.interest_free_days.on_holidays and any(holiday.date == date for holiday in self.applied_holidays):
            return False
        return True
