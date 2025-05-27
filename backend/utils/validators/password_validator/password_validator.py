from backend.utils.validators.password_validator.rules import (
    BaseRule,
    DigitRule,
    LowercaseRule,
    MaxLengthRule,
    MinLengthRule,
    NoSpaceRule,
    SpecialCharRule,
    UppercaseRule,
)


class PasswordValidator:
    def __init__(self) -> None:
        self.rules: list[BaseRule] = []
        self.negate_next = False

    def min(self, length: int) -> 'PasswordValidator':
        self.rules.append(MinLengthRule(length, self.negate_next))
        self.negate_next = False
        return self

    def max(self, length: int) -> 'PasswordValidator':
        self.rules.append(MaxLengthRule(length, self.negate_next))
        self.negate_next = False
        return self

    def no(self) -> 'PasswordValidator':
        self.negate_next = True
        return self

    def uppercase(self) -> 'PasswordValidator':
        self.rules.append(UppercaseRule(self.negate_next))
        self.negate_next = False
        return self

    def lowercase(self) -> 'PasswordValidator':
        self.rules.append(LowercaseRule(self.negate_next))
        self.negate_next = False
        return self

    def digits(self) -> 'PasswordValidator':
        self.rules.append(DigitRule(self.negate_next))
        self.negate_next = False
        return self

    def spaces(self) -> 'PasswordValidator':
        self.rules.append(NoSpaceRule(not self.negate_next))  # Inverted logic for NoSpaceRule
        self.negate_next = False
        return self

    def special_char(self, special_chars: str = '!@#$%^&*') -> 'PasswordValidator':
        self.rules.append(SpecialCharRule(special_chars, self.negate_next))
        self.negate_next = False
        return self

    def validate(self, password: str, raise_exceptions: bool = False) -> bool:
        if raise_exceptions:
            for rule in self.rules:
                rule.validate(password)
            return True
        else:
            return all(rule.validate(password) for rule in self.rules)
