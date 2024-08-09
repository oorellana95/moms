import datetime
import enum

import pydantic
from project.domain.models.products.loan import model as loan_model, builder as loan_builder


class LoanPaymentPeriodicityDto(str, enum.Enum):
    DAILY = "DAILY",
    WEEKLY = "WEEKLY",
    FORTNIGHTLY = "FORTNIGHTLY"
    MONTHLY = "MONTHLY"

    @property
    def days(self) -> int:
        days_map = {
            LoanPaymentPeriodicityDto.DAILY: 1,
            LoanPaymentPeriodicityDto.WEEKLY: 7,
            LoanPaymentPeriodicityDto.FORTNIGHTLY: 15,
            LoanPaymentPeriodicityDto.MONTHLY: 30
        }
        return days_map[self]


class LoanAllowedTermDto(enum.Enum):
    MONTH = "MONTH"
    BIMONTH = "BIMONTH"

    @property
    def days(self) -> int:
        days_map = {
            LoanAllowedTermDto.MONTH: 30,
            LoanAllowedTermDto.BIMONTH: 60
        }
        return days_map[self]


class GenerateLoanEstimateDto(pydantic.BaseModel):
    principal: int
    monthly_interest_rate: float
    term: LoanAllowedTermDto
    first_payment_date: datetime.date
    payment_periodicity: LoanPaymentPeriodicityDto
    interest_free_days: loan_model.InterestFreeDays

    @pydantic.field_validator('principal')
    def validate_principal(cls, value):
        if value < 50000:
            raise ValueError('Principal must be greater than 50,000')
        return value

    def build_new_loan_data(self) -> loan_builder.CreateNewLoanData:
        """Convert DTO to CreateLoanInputData with transformed fields."""
        data = self.model_dump()
        data.update({
            "term_in_days": self.term.days,
            "payment_periodicity_in_days": self.payment_periodicity.days,
        })
        return loan_builder.CreateNewLoanData(**data)

