# conftest.py

import pytest


# инициализационный хук pytest для CLI и ini
def pytest_addoption(parser):
    # добавляем опцию --env для запуска, а также дефолтные значения price/quantity для демонстрации pytestconfig.getini
    # parser - объект, отвечающий за CLI options, доступен в рамках данного хука
    parser.addoption("--env", action="store", default="local", help="Test environment")
    parser.addini("default_base_price", "Default base price for tests", default="10")
    parser.addini("default_quantity", "Default quantity for tests", default="1")

# этот хук автоматически вызывается pytest перед каждым тестом
def pytest_runtest_setup(item):
    # в хуке прописываем пропуск тестов с меткой "skip_on_ci" при условии опции запуска --env = ci
    if "skip_on_ci" in item.keywords and item.config.getoption("--env") == "ci":
        pytest.skip("Пропускаем, поскольку указана опция --env=ci")


# --- фикстуры для демонстрации scope ---

@pytest.fixture(scope="session")
def env(pytestconfig):
    # возвращает значение env из командной строки в рамках сессии
    return pytestconfig.getoption("--env")


@pytest.fixture(scope="module")
def counter():
    # счётчик, который сохраняет состояние между тестами в рамках модуля
    state = {"value": 0}
    return state


# --- несколько фикстур-флагов, которые будем использовать с lazy_fixture ---

@pytest.fixture
def flag_none():
    print("\n[SETUP]") # необходима опция запуска -s для вывода принтов
    flag = {}
    yield flag
    print("\n[TEARDOWN]")

@pytest.fixture
def flag_student():
    print("\n[SETUP]")
    flag = {"is_student": True}
    yield flag
    print("\n[TEARDOWN]")

@pytest.fixture
def flag_bulk_large():
    print("\n[SETUP]")
    flag = {"is_bulk_order": True}
    yield flag
    print("\n[TEARDOWN]")

@pytest.fixture
def flag_coupon():
    print("\n[SETUP]")
    flag = {"has_coupon": True}
    yield flag
    print("\n[TEARDOWN]")

@pytest.fixture
def flag_express_and_gift():
    print("\n[SETUP]")
    flag = {"is_express_delivery": True, "is_gift_wrapping": True}
    yield flag
    print("\n[TEARDOWN]")

@pytest.fixture
def flag_many_discounts():
    print("\n[SETUP]")
    flag = {
        "is_student": True,
        "is_holiday": True,
        "is_first_purchase": True,
        "is_member": True,
        "is_eco_friendly": True,
        "is_referral": True
    }
    yield flag
    print("\n[TEARDOWN]")


# фикстура для демонстрации usefixtures для тестового класса
@pytest.fixture
def setup_and_teardown():
    print("\n[SETUP for usefixtures]")
    yield
    print("\n[TEARDOWN for usefixtures]")


# autouse fixture — выполняется для каждого теста автоматически
@pytest.fixture(autouse=True)
def auto_log_test(request):
    test_name = request.node.name
    print(f"\n--- START TEST: {test_name} ---")
    yield
    print(f"\n--- END TEST: {test_name} ---")