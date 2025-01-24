import pytest
from users.tests.helpers import assert_password_common, assert_password_valid


class TestCommonPasswordValidator:
    @pytest.mark.parametrize("password", [
        'password123',
        'admin123', 
        'welcome123',
        'test123',
        'user123',
        'qwerty123',
    ])
    def test_simple_common_passwords(self, password_validator, password):
        """Simple common passwords with numbers"""
        assert_password_common(password_validator, password)

    @pytest.mark.parametrize("password", [
        'Password123',
        'ADMIN123',
        'Welcome123', 
        'TeSt123',
        'UsEr123',
    ])
    def test_case_variations(self, password_validator, password):
        """Common passwords with mixed case variations"""
        assert_password_common(password_validator, password)

    @pytest.mark.parametrize("password", [
        'p@ssword123',
        'p@ssw0rd123',
        '@dm1n123',
        'w3lc0me123',
        't3st123',
    ])
    def test_leet_speak_variations(self, password_validator, password):
        """Common passwords using leet speak substitutions"""
        assert_password_common(password_validator, password)

    @pytest.mark.parametrize("password", [
        'password!!!',
        '!!!password!!!',
        'admin###',
        '###admin###',
        'welcome!!!123',
    ])
    def test_special_character_padding(self, password_validator, password):
        """Common passwords with special character padding"""
        assert_password_common(password_validator, password)

    @pytest.mark.parametrize("password", [
        'Tr0ub4dor&3',
        'correcthorsebatterystaple',
        'MyDog8MyHomework!',
        'Butterfly$123Garden',
    ])
    def test_valid_passwords(self, password_validator, password):
        """Complex, unique passwords that should pass validation"""
        assert_password_valid(password_validator, password)

    @pytest.mark.parametrize("password,should_fail", [
        ('', False),
        ('!@#$%^&*()', False),
        ('12345678', False),
        ('!@#complex!@#', False),
    ])
    def test_edge_cases(self, password_validator, password, should_fail):
        """Edge cases testing empty strings, special chars only, numbers only, etc"""
        if should_fail or any(base in password.lower() for base in password_validator.common_bases):
            assert_password_common(password_validator, password)
        else:
            assert_password_valid(password_validator, password)  