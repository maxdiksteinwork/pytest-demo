# src/discount_calculator.py

class DiscountCalculator:
    def __init__(self, base_price, quantity):
        self.base_price = base_price
        self.quantity = quantity

    def calculate_total(self, **flags):
        if self.base_price < 0:
            raise ValueError()

        total = self.base_price * self.quantity

        if flags.get('is_student'):
            total *= 0.9
        if flags.get('is_holiday'):
            total *= 0.95
        if flags.get('is_first_purchase'):
            total *= 0.85
        if flags.get('is_bulk_order') and self.quantity > 10:
            total *= 0.8
        if flags.get('is_member'):
            total *= 0.93
        if flags.get('is_eco_friendly'):
            total *= 0.97
        if flags.get('is_referral'):
            total *= 0.92

        if flags.get('is_express_delivery'):
            total *= 1.1
        if flags.get('is_gift_wrapping'):
            total *= 1.05
        if flags.get('is_peak_season'):
            total *= 1.12

        if flags.get('has_coupon'):
            total -= 50

        return max(total, 0)