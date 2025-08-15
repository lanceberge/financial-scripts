import pandas as pd

# Default parameters
home_price = 500_000
purchase_discount = 0.2
appreciation_pct = 0.05
expense_vacancy_cost = 0.4
loan_pct = 0.0753
rent_income_pct = 0.008
pct_down = 0.2
rental_appreciation_pct = 0.05
YEARS = 10
PRINCIPAL_PAYDOWN_PCT = 0.015


def calculate_returns(
    home_price=home_price,
    purchase_discount=purchase_discount,
    appreciation_pct=appreciation_pct,
    expense_vacancy_cost=expense_vacancy_cost,
    loan_pct=loan_pct,
    rent_income_pct=rent_income_pct,
    pct_down=pct_down,
    rental_appreciation_pct=rental_appreciation_pct,
    years=YEARS,
    principal_paydown_pct=PRINCIPAL_PAYDOWN_PCT,
):
    # Calculate initial values
    purchase_price = home_price * (1 - purchase_discount)
    down_payment = purchase_price * pct_down
    loan_amount = purchase_price * (1 - pct_down)
    rental_income_amt = purchase_price * rent_income_pct * 12

    # Lists to store annual results and track cumulative values for CAGR
    annual_roi = []
    cumulative_cash_flow = 0
    current_home_price = purchase_price
    current_rental_income = rental_income_amt
    remaining_principal = loan_amount

    for year in range(years):
        # Gains
        home_appreciation = current_home_price * appreciation_pct
        principal_paydown_amt = purchase_price * principal_paydown_pct
        gross_rental_cash_flow = current_rental_income * (1 - expense_vacancy_cost)

        interest_cost = remaining_principal * loan_pct
        net_rental_cash_flow = gross_rental_cash_flow - interest_cost

        # Total annual return
        total_return = home_appreciation + principal_paydown_amt + net_rental_cash_flow
        roi = total_return / down_payment * 100

        # Update for next year
        current_home_price *= 1 + appreciation_pct
        current_rental_income *= 1 + rental_appreciation_pct
        remaining_principal -= principal_paydown_amt
        cumulative_cash_flow += net_rental_cash_flow

        # Store results
        annual_roi.append(f"{roi:.1f}%")

    # Calculate CAGR
    # TODO should just be total return divided by total invested
    ending_value = current_home_price - remaining_principal + cumulative_cash_flow
    beginning_value = down_payment
    cagr = (
        ((ending_value / beginning_value) ** (1 / years) - 1) * 100
        if beginning_value > 0
        else 0
    )

    return annual_roi, f"{cagr:.1f}%"


def make_scenario_calculator(**scenario_params):
    def scenario_calculator():
        return calculate_returns(**scenario_params)

    return scenario_calculator


scenarios = {
    "Default": make_scenario_calculator(),
    "No Purchase Discount": make_scenario_calculator(purchase_discount=0.0),
    "1.2% Rental Income": make_scenario_calculator(rent_income_pct=0.012),
    "7% Appreciation": make_scenario_calculator(appreciation_pct=0.07),
    "3% Appreciation": make_scenario_calculator(appreciation_pct=0.03),
    "-3% Appreciation": make_scenario_calculator(appreciation_pct=-0.03),
    "20% Expense/Vacancy": make_scenario_calculator(expense_vacancy_cost=0.2),
    "60% Expense/Vacancy": make_scenario_calculator(expense_vacancy_cost=0.6),
    "5% Loan Rate": make_scenario_calculator(loan_pct=0.05),
    "9% Loan Rate": make_scenario_calculator(loan_pct=0.09),
    "5% Down Payment": make_scenario_calculator(pct_down=0.05),
    "5% Down Payment": make_scenario_calculator(pct_down=0.05),
    "3% Principal Paydown Pct": make_scenario_calculator(principal_paydown_pct=0.03),
}

results = {name: calc()[0] for name, calc in scenarios.items()}
cagr_values = {name: calc()[1] for name, calc in scenarios.items()}

df = pd.DataFrame(results, index=[f"Year {i+1}" for i in range(YEARS)]).transpose()

df["CAGR"] = pd.Series(cagr_values).round(2)

print("\nAnnual ROI (%) and CAGR (%):")
print(df)
