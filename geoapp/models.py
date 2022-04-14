import enum


class Gender(str, enum.Enum):
    Female = "F"
    Male = "M"


class Age(str, enum.Enum):
    LessThan25 = "<=24"
    Between25And34 = "25-34"
    Between35And44 = "35-44"
    Between45And54 = "45-54"
    Between55And64 = "55-64"
    MoreThan64 = ">=65"
