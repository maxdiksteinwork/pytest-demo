# tests/test_discount_calculator.py

import random
import warnings
import pytest
from pytest_lazyfixture import lazy_fixture
from src.discount_calculator import DiscountCalculator


# функция, дублирующая суть discount_calculator
# чтобы мы при тестировании сравнивали "стороннее" значение total со значением total объекта DiscountCalculator
def compute_expected(base_price, quantity, flags):
    total = base_price * quantity
    if flags.get('is_student'):
        total *= 0.9
    if flags.get('is_holiday'):
        total *= 0.95
    if flags.get('is_first_purchase'):
        total *= 0.85
    if flags.get('is_bulk_order') and quantity > 10:
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


# тест без флагов
def test_basic_total_no_flags():
    calc = DiscountCalculator(10.0, 3)
    assert calc.calculate_total() == pytest.approx(30.0)


# параметризация с разными флагами и множителями, проверка на корректность применения отдельного флага к общей сумме
@pytest.mark.parametrize("flag, multiplier", [
    ({"is_student": True}, 0.9),
    ({"is_holiday": True}, 0.95),
    ({"is_first_purchase": True}, 0.85),
    ({"is_member": True}, 0.93),
    ({"is_eco_friendly": True}, 0.97),
    ({"is_referral": True}, 0.92),
    ({"is_express_delivery": True}, 1.1),
    ({"is_gift_wrapping": True}, 1.05),
    ({"is_peak_season": True}, 1.12),
])
def test_single_flag_multiplier(flag, multiplier):
    base, qty = 50.0, 2
    calc = DiscountCalculator(base, qty)
    expected = base * qty * multiplier
    assert calc.calculate_total(**flag) == pytest.approx(expected)


# использование usefixtures на уровне класса
@pytest.mark.usefixtures("setup_and_teardown")
class TestWithSetup:
    def test_coupon_applies(self):
        calc = DiscountCalculator(40.0, 1)
        # купон отнимает от итоговой стоимости 50, результат должен быть max(0, -10) => 0
        assert calc.calculate_total(has_coupon=True) == 0

    def test_bulk_order_applies_only_if_large_quantity(self):
        calc_small = DiscountCalculator(10, 5)
        # при данном флаге quantity должно быть > 10, чтобы скидка применилась, в данном случае total будет без скидки
        assert calc_small.calculate_total(is_bulk_order=True) == 50
        calc_big = DiscountCalculator(10, 11)
        expected = compute_expected(10, 11, {"is_bulk_order": True})
        # quantity 11 - скидка есть при проверяемом флаге
        assert calc_big.calculate_total(is_bulk_order=True) == pytest.approx(expected)


# параметризация с lazy_fixture
@pytest.mark.parametrize("flags", [
    lazy_fixture("flag_none"),
    lazy_fixture("flag_student"),
    lazy_fixture("flag_bulk_large"),
    lazy_fixture("flag_coupon"),
    lazy_fixture("flag_express_and_gift"),
    lazy_fixture("flag_many_discounts"),
], ids=["none", "student", "bulk_large", "coupon", "express+gift", "many_discounts"])
def test_various_flag_combinations(flags):
    base, qty = 20.0, 12
    calc = DiscountCalculator(base, qty)
    expected = compute_expected(base, qty, flags)
    assert calc.calculate_total(**flags) == pytest.approx(expected)


# ---------------- демонстрация xfail, skip, fail ----------------

@pytest.mark.xfail(reason="Демонстрация xfail: ожидаем несоответствие", strict=False)
def test_known_edge_case_xfail():
    calc = DiscountCalculator(10, 1)
    assert calc.calculate_total(has_coupon=True) == -40  # assert провалится - будет xfail


@pytest.mark.skip(reason="Демонстрационно пропускаем тест")
def test_skipped_example():
    pytest.fail("Этот тест пропущен, он не должен выполняться")


def test_fail_force_example():    
    pytest.fail("Искусственная ошибка") # роняем тест
    

# демонстрация approx
def test_many_decimal_discounts():
    calc = DiscountCalculator(19.99, 3)
    flags = {"is_student": True, "is_eco_friendly": True}
    expected = compute_expected(19.99, 3, flags)
    assert calc.calculate_total(**flags) == pytest.approx(expected, rel=1e-6)


# использование фикстуры env и встроенных фикстур pytestconfig, request
def test_env_and_request_and_pytestconfig(pytestconfig, request, env):
    default_base = pytestconfig.getini("default_base_price") # pytestconfig - конфигурация pytest (CLI, ini)
    assert request.node.name.startswith("test_") # request - информация о текущем тесте (имя, параметры и т.д.)
    assert isinstance(env, str)
    assert default_base is not None


# демонстрация monkeypatch для подмены функции
def test_monkeypatch_override(monkeypatch):
    def fake_calc(self, **flags):
        return 12345.678
    monkeypatch.setattr(DiscountCalculator, "calculate_total", fake_calc, raising=True)

    calc = DiscountCalculator(1, 1)
    assert calc.calculate_total() == pytest.approx(12345.678)


# демонстрация перезапуска флаки-теста
@pytest.mark.flaky(reruns=2)
def test_flaky_example():
    if random.random() < 0.3:
        pytest.fail("Ошибка, нужен перезапуск. Если видите это сообщение - перезапусков не хватило :)")
    assert True


# демонстрация пропуска теста с соответствующей меткой
@pytest.mark.skip_on_ci
def test_skip_on_ci_demo():
    # этот тест будет пропущен, если pytest запущен с --env=ci
    assert True


# тест предупреждений через pytest.warns
def test_warns_example():
    # проверяем, имеется ли в коде под контекстным менеджером нужное нам предупреждение
    with pytest.warns(UserWarning, match="deprecated") as record:
        # генерируем нужное нам предупреждение
        warnings.warn("This feature is deprecated", UserWarning)

    # record - список пойманных WarningMessage
    for w in record:
        print(f"[WARN CAPTURED] {w.message} (категория: {w.category.__name__})")

    # проверим, что хотя бы одно предупреждение было
    assert any("deprecated" in str(w.message) for w in record)


# ---------------- демонстрация фикстуры со scope = module ----------------

def test_counter_increment(counter):
    counter["value"] += 1
    assert counter["value"] == 1

def test_counter_increment_again(counter):
    # значение сохраняется из предыдущего теста
    counter["value"] += 2
    assert counter["value"] == 3


# ---------------- негативные тесты ----------------

def test_negative_base_price_raises():
    # проверяем, что при отрицательной цене бросается ValueError
    calc = DiscountCalculator(-10, 1)
    with pytest.raises(ValueError):
        calc.calculate_total()


def test_invalid_flag_is_ignored():
    # проверяем, что при передаче невалидного флага, он игнорируется и функция класса отрабатывает корректно
    base, qty = 10.0, 2
    calc = DiscountCalculator(base, qty)

    # без флага
    expected = calc.calculate_total()
    # с невалидным флагом
    result_with_invalid = calc.calculate_total(is_fictional_flag=True)

    # значение скидки без флага должно совпадать со значением скидки с невалидным флагом (он проигнорирован)
    assert result_with_invalid == expected
