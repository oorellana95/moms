import datetime
from typing import Dict, Any, List

import pydantic


class Holiday(pydantic.BaseModel):
    description: str
    date: datetime.date


_COLOMBIAN_HOLIDAYS_DATA = {
    "fixed": [
        {"month": 1, "day": 1, "description": "Año Nuevo"},
        {"month": 5, "day": 1, "description": "Día del trabajo"},
        {"month": 7, "day": 20, "description": "Día de la independencia de Colombia"},
        {"month": 8, "day": 7, "description": "Batalla de Boyacá"},
        {"month": 12, "day": 8, "description": "Inmaculada Concepción"},
        {"month": 12, "day": 25, "description": "Navidad"},
    ],
    "variable":
        {
            "based_on_specific_day": [
                {"month": 1, "day": 6, "description": "Reyes Magos", "apply_law51": True},
                {"month": 3, "day": 19, "description": "Día de San José", "apply_law51": True},
                {"month": 6, "day": 29, "description": "San Pedro y San Pablo", "apply_law51": True},
                {"month": 8, "day": 15, "description": "Asunción de la Virgen", "apply_law51": True},
                {"month": 10, "day": 12, "description": "Día de la raza", "apply_law51": True},
                {"month": 11, "day": 1, "description": "Todos los santos", "apply_law51": True},
                {"month": 11, "day": 11, "description": "Independencia de Cartagena", "apply_law51": True},
            ],
            "based_on_easter": [
                {"description": "Jueves Santo", "offset": -3, "apply_law51": False},
                {"description": "Viernes Santo", "offset": -2, "apply_law51": False},
                {"description": "Ascensión de Jesus", "offset": 39, "apply_law51": True},
                {"description": "Corpus Christi", "offset": 60, "apply_law51": True},
                {"description": "Sagrado Corazón de Jesús", "offset": 68, "apply_law51": True}
            ]
        }
}


class ColombianHolidaysCalculator:
    def __init__(self):
        self.holidays_data = _COLOMBIAN_HOLIDAYS_DATA

    def calculate(self, year: int) -> List[Holiday]:
        fixed_holidays = self.holidays_data["fixed"]
        variable_holidays = self._calculate_variable_holidays(year=year, holidays=self.holidays_data["variable"])
        holidays = fixed_holidays + variable_holidays
        return self._map_holidays(year=year, holidays=holidays)

    @staticmethod
    def calculate_easter(year: int) -> datetime.date:
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        month = (h + l - 7 * m + 114) // 31
        day = ((h + l - 7 * m + 114) % 31) + 1

        return datetime.date(year=year, month=month, day=day)

    @staticmethod
    def _map_holidays(year: int, holidays: List[Dict[str, Any]]) -> List[Holiday]:
        sorted_holidays = sorted(holidays, key=lambda h: (h["month"], h["day"]))
        return [
            Holiday(
                description=holiday["description"],
                date=datetime.date(
                    year=year,
                    month=holiday["month"],
                    day=holiday["day"]
                )
            ) for holiday in sorted_holidays
        ]

    def _calculate_variable_holidays(self, year: int, holidays: Dict[str, Any]) -> List[Dict[str, Any]]:
        base_specific_day_holidays = holidays["based_on_specific_day"]
        base_easter_holidays = self._calculate_holidays_based_on_easter(year=year, holidays=holidays["based_on_easter"])
        variable_holidays = base_easter_holidays + base_specific_day_holidays
        return self._apply_law51(year=year, holidays=variable_holidays)

    def _calculate_holidays_based_on_easter(self, year: int, holidays: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        easter_date = self.calculate_easter(year=year)
        for holiday in holidays:
            holiday["month"] = (easter_date + datetime.timedelta(days=holiday["offset"])).month
            holiday["day"] = (easter_date + datetime.timedelta(days=holiday["offset"])).day
        return holidays

    @staticmethod
    def _apply_law51(year: int, holidays: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for holiday in holidays:
            if holiday["apply_law51"]:
                holiday_date = datetime.date(year, holiday["month"], holiday["day"])
                if holiday_date.weekday() != 0:
                    days_to_monday = (7 - holiday_date.weekday()) % 7
                    holiday_date += datetime.timedelta(days=days_to_monday)
                    holiday["month"] = holiday_date.month
                    holiday["day"] = holiday_date.day
        return holidays
