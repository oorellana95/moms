from typing import Dict, Any

from project.commons import holidays
from project.domain.models.products.loan import model as loan_model, builder as loan_builder, payments_resolver
from project.services.product_loan import model as service_model


def create_estimation_for_loan(request: Dict[str, Any]) -> loan_model.Loan:
    validated_request = _validate_request(request=request)
    builder = _prepare_builder(request=validated_request)
    return builder.create_new_loan(create_new_loan_data=validated_request.build_new_loan_data())


def _validate_request(request: Dict[str, Any]) -> service_model.GenerateLoanEstimateDto:
    return service_model.GenerateLoanEstimateDto.model_validate(request)


def _prepare_builder(request: service_model.GenerateLoanEstimateDto):
    year = request.first_payment_date.year
    calculator = holidays.ColombianHolidaysCalculator()
    applied_holidays = calculator.calculate(year=year) + calculator.calculate(year=year+1)
    resolver_settings = payments_resolver.ResolverSettings(
        interest_free_days=request.interest_free_days,
        applied_holidays=applied_holidays
    )
    resolver = payments_resolver.LoanPaymentsResolver(settings=resolver_settings)
    return loan_builder.LoanBuilder(payments_resolver=resolver)

