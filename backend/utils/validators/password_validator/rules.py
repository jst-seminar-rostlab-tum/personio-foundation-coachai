class RuleError(Exception):
    pass


class BaseRule:
    def __init__(self, negate: bool = False) -> None:
        self.negate = negate

    def check(self, password: str) -> bool:
        raise NotImplementedError

    def error_message(self) -> str:
        return 'Password validation failed.'

    def validate(self, password: str) -> bool:
        result = self.check(password)
        if self.negate:
            result = not result
        if not result:
            raise RuleError(self.error_message())
        return True


class MinLengthRule(BaseRule):
    def __init__(self, length: int, negate: bool = False) -> None:
        super().__init__(negate)
        self.length = length

    def check(self, password: str) -> bool:
        return len(password) >= self.length

    def error_message(self) -> str:
        return f'Password must be at least {self.length} characters long.'


class MaxLengthRule(BaseRule):
    def __init__(self, length: int, negate: bool = False) -> None:
        super().__init__(negate)
        self.length = length

    def check(self, password: str) -> bool:
        return len(password) <= self.length

    def error_message(self) -> str:
        return f'Password must be at most {self.length} characters long.'


class UppercaseRule(BaseRule):
    def check(self, password: str) -> bool:
        return any(c.isupper() for c in password)

    def error_message(self) -> str:
        return 'Password must contain at least one uppercase letter.'


class LowercaseRule(BaseRule):
    def check(self, password: str) -> bool:
        return any(c.islower() for c in password)

    def error_message(self) -> str:
        return 'Password must contain at least one lowercase letter.'


class DigitRule(BaseRule):
    def check(self, password: str) -> bool:
        return any(c.isdigit() for c in password)

    def error_message(self) -> str:
        return 'Password must contain at least one digit.'


class NoSpaceRule(BaseRule):
    def check(self, password: str) -> bool:
        return ' ' not in password

    def error_message(self) -> str:
        return 'Password must not contain spaces.'


class SpecialCharRule(BaseRule):
    def __init__(self, special_chars: str, negate: bool = False) -> None:
        super().__init__(negate)
        self.special_chars = special_chars

    def check(self, password: str) -> bool:
        return any(c in self.special_chars for c in password)

    def error_message(self) -> str:
        return f'Password must contain at least one special character ({self.special_chars}).'
