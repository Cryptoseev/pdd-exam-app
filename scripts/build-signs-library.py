#!/usr/bin/env python3
"""
Build the road signs library from questions.json data.
Extracts sign codes, categories, names and associated questions.

Usage: python3 scripts/build-signs-library.py
Output: data/signsLibrary.json
"""

import json
import re
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
QUESTIONS_JSON = PROJECT_DIR / "data/questions.json"
OUTPUT = PROJECT_DIR / "data/signsLibrary.json"

# ── Russian ПДД sign catalog ──────────────────────────────────────────────────
# Categories per ГОСТ Р 52289
SIGN_CATALOG = {
    # 1.x — Предупреждающие (Warning)
    "1.1":  {"name": "Железнодорожный переезд со шлагбаумом",    "category": "warning"},
    "1.2":  {"name": "Железнодорожный переезд без шлагбаума",    "category": "warning"},
    "1.3":  {"name": "Однопутная железная дорога",               "category": "warning"},
    "1.3.1": {"name": "Однопутная железная дорога",              "category": "warning"},
    "1.3.2": {"name": "Многопутная железная дорога",             "category": "warning"},
    "1.4":  {"name": "Приближение к железнодорожному переезду",  "category": "warning"},
    "1.5":  {"name": "Пересечение с трамвайной линией",          "category": "warning"},
    "1.6":  {"name": "Пересечение равнозначных дорог",           "category": "warning"},
    "1.7":  {"name": "Пересечение с круговым движением",         "category": "warning"},
    "1.8":  {"name": "Светофорное регулирование",                "category": "warning"},
    "1.9":  {"name": "Разводной мост",                           "category": "warning"},
    "1.10": {"name": "Выезд на набережную",                      "category": "warning"},
    "1.11": {"name": "Опасный поворот",                          "category": "warning"},
    "1.11.1": {"name": "Опасный поворот направо",               "category": "warning"},
    "1.11.2": {"name": "Опасный поворот налево",                 "category": "warning"},
    "1.12": {"name": "Опасные повороты",                         "category": "warning"},
    "1.12.1": {"name": "Опасные повороты (начало с правого)",    "category": "warning"},
    "1.12.2": {"name": "Опасные повороты (начало с левого)",     "category": "warning"},
    "1.13": {"name": "Крутой спуск",                             "category": "warning"},
    "1.14": {"name": "Крутой подъём",                            "category": "warning"},
    "1.15": {"name": "Скользкая дорога",                         "category": "warning"},
    "1.16": {"name": "Неровная дорога",                          "category": "warning"},
    "1.17": {"name": "Искусственная неровность",                 "category": "warning"},
    "1.18": {"name": "Выброс гравия",                            "category": "warning"},
    "1.19": {"name": "Опасная обочина",                          "category": "warning"},
    "1.20": {"name": "Сужение дороги",                           "category": "warning"},
    "1.20.1": {"name": "Сужение справа",                         "category": "warning"},
    "1.20.2": {"name": "Сужение слева",                          "category": "warning"},
    "1.20.3": {"name": "Сужение с обеих сторон",                 "category": "warning"},
    "1.21": {"name": "Двустороннее движение",                    "category": "warning"},
    "1.22": {"name": "Выезд на дорогу с односторонним движением", "category": "warning"},
    "1.23": {"name": "Пешеходный переход",                       "category": "warning"},
    "1.23.1": {"name": "Дети",                                   "category": "warning"},
    "1.24": {"name": "Пересечение с велосипедной дорожкой",      "category": "warning"},
    "1.25": {"name": "Дорожные работы",                          "category": "warning"},
    "1.26": {"name": "Перегон скота",                            "category": "warning"},
    "1.27": {"name": "Дикие животные",                           "category": "warning"},
    "1.28": {"name": "Падение камней",                           "category": "warning"},
    "1.29": {"name": "Боковой ветер",                            "category": "warning"},
    "1.30": {"name": "Низколетящие самолёты",                    "category": "warning"},
    "1.31": {"name": "Тоннель",                                  "category": "warning"},
    "1.32": {"name": "Затор",                                    "category": "warning"},
    "1.33": {"name": "Прочие опасности",                         "category": "warning"},

    # 2.x — Приоритет (Priority)
    "2.1":  {"name": "Главная дорога",                           "category": "priority"},
    "2.2":  {"name": "Конец главной дороги",                     "category": "priority"},
    "2.3":  {"name": "Пересечение с второстепенной дорогой",     "category": "priority"},
    "2.3.1": {"name": "Примыкание второстепенной дороги справа", "category": "priority"},
    "2.3.2": {"name": "Примыкание второстепенной дороги слева",  "category": "priority"},
    "2.4":  {"name": "Уступите дорогу",                          "category": "priority"},
    "2.5":  {"name": "Движение без остановки запрещено",         "category": "priority"},
    "2.6":  {"name": "Преимущество встречного движения",         "category": "priority"},
    "2.7":  {"name": "Преимущество перед встречным движением",   "category": "priority"},

    # 3.x — Запрещающие (Prohibitory)
    "3.1":  {"name": "Въезд запрещён",                           "category": "prohibitory"},
    "3.2":  {"name": "Движение запрещено",                       "category": "prohibitory"},
    "3.3":  {"name": "Движение механических ТС запрещено",       "category": "prohibitory"},
    "3.4":  {"name": "Движение грузовых автомобилей запрещено",  "category": "prohibitory"},
    "3.5":  {"name": "Движение мотоциклов запрещено",            "category": "prohibitory"},
    "3.6":  {"name": "Движение тракторов запрещено",             "category": "prohibitory"},
    "3.7":  {"name": "Движение с прицепом запрещено",            "category": "prohibitory"},
    "3.8":  {"name": "Движение гужевых повозок запрещено",       "category": "prohibitory"},
    "3.9":  {"name": "Движение на велосипедах запрещено",        "category": "prohibitory"},
    "3.10": {"name": "Движение пешеходов запрещено",             "category": "prohibitory"},
    "3.11": {"name": "Ограничение массы",                        "category": "prohibitory"},
    "3.12": {"name": "Ограничение нагрузки на ось",              "category": "prohibitory"},
    "3.13": {"name": "Ограничение высоты",                       "category": "prohibitory"},
    "3.14": {"name": "Ограничение ширины",                       "category": "prohibitory"},
    "3.15": {"name": "Ограничение длины",                        "category": "prohibitory"},
    "3.16": {"name": "Ограничение минимальной дистанции",        "category": "prohibitory"},
    "3.17": {"name": "Таможня",                                  "category": "prohibitory"},
    "3.17.1": {"name": "Таможня",                                "category": "prohibitory"},
    "3.17.2": {"name": "Опасность",                              "category": "prohibitory"},
    "3.17.3": {"name": "Контроль",                               "category": "prohibitory"},
    "3.18": {"name": "Поворот направо запрещён",                 "category": "prohibitory"},
    "3.18.1": {"name": "Поворот направо запрещён",               "category": "prohibitory"},
    "3.18.2": {"name": "Поворот налево запрещён",                "category": "prohibitory"},
    "3.19": {"name": "Разворот запрещён",                        "category": "prohibitory"},
    "3.20": {"name": "Обгон запрещён",                           "category": "prohibitory"},
    "3.21": {"name": "Конец зоны запрета обгона",                "category": "prohibitory"},
    "3.22": {"name": "Обгон грузовым автомобилям запрещён",      "category": "prohibitory"},
    "3.23": {"name": "Конец зоны запрета обгона для грузовых",   "category": "prohibitory"},
    "3.24": {"name": "Ограничение максимальной скорости",        "category": "prohibitory"},
    "3.25": {"name": "Конец зоны ограничения максимальной скорости", "category": "prohibitory"},
    "3.26": {"name": "Подача звукового сигнала запрещена",       "category": "prohibitory"},
    "3.27": {"name": "Остановка запрещена",                      "category": "prohibitory"},
    "3.28": {"name": "Стоянка запрещена",                        "category": "prohibitory"},
    "3.29": {"name": "Стоянка запрещена по нечётным числам месяца", "category": "prohibitory"},
    "3.30": {"name": "Стоянка запрещена по чётным числам месяца", "category": "prohibitory"},
    "3.31": {"name": "Конец зоны всех ограничений",              "category": "prohibitory"},
    "3.32": {"name": "Движение ТС с опасными грузами запрещено", "category": "prohibitory"},
    "3.33": {"name": "Движение ТС с взрывчатыми веществами запрещено", "category": "prohibitory"},
    "3.37": {"name": "Движение мопедов запрещено",               "category": "prohibitory"},

    # 4.x — Предписывающие (Mandatory)
    "4.1":  {"name": "Движение прямо",                           "category": "mandatory"},
    "4.1.1": {"name": "Движение прямо",                          "category": "mandatory"},
    "4.1.2": {"name": "Движение направо",                        "category": "mandatory"},
    "4.1.3": {"name": "Движение налево",                         "category": "mandatory"},
    "4.1.4": {"name": "Движение прямо или направо",              "category": "mandatory"},
    "4.1.5": {"name": "Движение прямо или налево",               "category": "mandatory"},
    "4.1.6": {"name": "Движение направо или налево",             "category": "mandatory"},
    "4.2":  {"name": "Объезд препятствия",                       "category": "mandatory"},
    "4.2.1": {"name": "Объезд препятствия справа",               "category": "mandatory"},
    "4.2.2": {"name": "Объезд препятствия слева",                "category": "mandatory"},
    "4.2.3": {"name": "Объезд препятствия справа или слева",     "category": "mandatory"},
    "4.3":  {"name": "Круговое движение",                        "category": "mandatory"},
    "4.4":  {"name": "Велосипедная дорожка",                     "category": "mandatory"},
    "4.5":  {"name": "Пешеходная дорожка",                       "category": "mandatory"},
    "4.6":  {"name": "Ограничение минимальной скорости",         "category": "mandatory"},
    "4.7":  {"name": "Конец зоны ограничения минимальной скорости", "category": "mandatory"},
    "4.8":  {"name": "Направление движения ТС с опасными грузами", "category": "mandatory"},

    # 5.x — Особые предписания (Special)
    "5.1":  {"name": "Автомагистраль",                           "category": "special"},
    "5.2":  {"name": "Конец автомагистрали",                     "category": "special"},
    "5.3":  {"name": "Дорога для автомобилей",                   "category": "special"},
    "5.4":  {"name": "Конец дороги для автомобилей",             "category": "special"},
    "5.5":  {"name": "Дорога с односторонним движением",         "category": "special"},
    "5.6":  {"name": "Конец дороги с односторонним движением",   "category": "special"},
    "5.7":  {"name": "Выезд на дорогу с односторонним движением", "category": "special"},
    "5.7.1": {"name": "Выезд на дорогу справа",                  "category": "special"},
    "5.7.2": {"name": "Выезд на дорогу слева",                   "category": "special"},
    "5.8":  {"name": "Реверсивное движение",                     "category": "special"},
    "5.9":  {"name": "Конец реверсивного движения",              "category": "special"},
    "5.10": {"name": "Выезд на дорогу с реверсивным движением",  "category": "special"},
    "5.11": {"name": "Дорога с полосой для маршрутных ТС",       "category": "special"},
    "5.11.1": {"name": "Дорога с полосой для маршрутных ТС",     "category": "special"},
    "5.12": {"name": "Конец дороги с полосой для маршрутных ТС", "category": "special"},
    "5.13": {"name": "Выезд на дорогу с полосой для маршрутных ТС", "category": "special"},
    "5.14": {"name": "Полоса для маршрутных ТС",                 "category": "special"},
    "5.15": {"name": "Направления движения по полосам",          "category": "special"},
    "5.16": {"name": "Начало полосы",                            "category": "special"},
    "5.17": {"name": "Конец полосы",                             "category": "special"},
    "5.18": {"name": "Направление движения по полосе",           "category": "special"},
    "5.19": {"name": "Пешеходный переход",                       "category": "special"},
    "5.19.1": {"name": "Пешеходный переход (правая сторона)",    "category": "special"},
    "5.19.2": {"name": "Пешеходный переход (левая сторона)",     "category": "special"},
    "5.20": {"name": "Искусственная неровность",                 "category": "special"},
    "5.21": {"name": "Жилая зона",                               "category": "special"},
    "5.22": {"name": "Конец жилой зоны",                         "category": "special"},
    "5.23": {"name": "Начало населённого пункта",                "category": "special"},
    "5.23.1": {"name": "Начало населённого пункта",              "category": "special"},
    "5.23.2": {"name": "Начало населённого пункта (на синем фоне)", "category": "special"},
    "5.24": {"name": "Конец населённого пункта",                 "category": "special"},
    "5.24.1": {"name": "Конец населённого пункта",               "category": "special"},
    "5.24.2": {"name": "Конец населённого пункта (на синем фоне)", "category": "special"},
    "5.25": {"name": "Начало населённого пункта (без ограничений)", "category": "special"},
    "5.26": {"name": "Конец населённого пункта (без ограничений)", "category": "special"},
    "5.27": {"name": "Зона с ограниченной стоянкой",             "category": "special"},
    "5.28": {"name": "Конец зоны с ограниченной стоянкой",       "category": "special"},
    "5.29": {"name": "Пешеходная зона",                          "category": "special"},
    "5.30": {"name": "Конец пешеходной зоны",                    "category": "special"},
    "5.31": {"name": "Зона с ограничением скорости",             "category": "special"},
    "5.32": {"name": "Конец зоны с ограничением скорости",       "category": "special"},
    "5.33": {"name": "Пешеходная и велосипедная дорожка",        "category": "special"},
    "5.34": {"name": "Конец пешеходной и велосипедной дорожки",  "category": "special"},

    # 6.x — Информационные (Informational)
    "6.1":  {"name": "Ограничение скорости (рекомендуемая)",     "category": "informational"},
    "6.2":  {"name": "Рекомендуемая скорость",                   "category": "informational"},
    "6.3":  {"name": "Место для разворота",                      "category": "informational"},
    "6.4":  {"name": "Место стоянки",                            "category": "informational"},
    "6.5":  {"name": "Полоса аварийной остановки",               "category": "informational"},
    "6.6":  {"name": "Подземный пешеходный переход",             "category": "informational"},
    "6.7":  {"name": "Надземный пешеходный переход",             "category": "informational"},
    "6.8":  {"name": "Тупик",                                    "category": "informational"},
    "6.9":  {"name": "Предварительный указатель направления",    "category": "informational"},
    "6.10": {"name": "Указатель направления",                    "category": "informational"},
    "6.11": {"name": "Указание расстояния до объекта",           "category": "informational"},
    "6.12": {"name": "Указатель расстояния",                     "category": "informational"},
    "6.13": {"name": "Километровый знак",                        "category": "informational"},
    "6.14": {"name": "Номер маршрута",                           "category": "informational"},
    "6.15": {"name": "Направление движения для грузовых авт.",   "category": "informational"},
    "6.16": {"name": "Общие ограничения скорости",               "category": "informational"},
}

CATEGORY_NAMES = {
    "warning":       "Предупреждающие знаки",
    "priority":      "Знаки приоритета",
    "prohibitory":   "Запрещающие знаки",
    "mandatory":     "Предписывающие знаки",
    "special":       "Знаки особых предписаний",
    "informational": "Информационные знаки",
}


def build_library():
    with open(QUESTIONS_JSON) as f:
        data = json.load(f)

    # Build index: sign_code → list of question_ids referencing it
    sign_questions: dict[str, list[str]] = {}

    for ticket in data["tickets"]:
        for q in ticket["questions"]:
            text = q["question"] + " " + q.get("explanation", "")
            codes = re.findall(r'\b(\d+\.\d+(?:\.\d+)?)\b', text)
            for code in codes:
                if code in SIGN_CATALOG:
                    if code not in sign_questions:
                        sign_questions[code] = []
                    qid = q["id"]
                    if qid not in sign_questions[code]:
                        sign_questions[code].append(qid)

    # Build library grouped by category
    library = {
        "categories": [],
        "signs": {}
    }

    # Collect signs by category
    by_category: dict[str, list] = {}
    for code, info in SIGN_CATALOG.items():
        cat = info["category"]
        if cat not in by_category:
            by_category[cat] = []
        sign_entry = {
            "code": code,
            "name": info["name"],
            "category": cat,
            "questionIds": sign_questions.get(code, []),
        }
        by_category[cat].append(sign_entry)
        library["signs"][code] = sign_entry

    # Categories list
    for cat_id, cat_name in CATEGORY_NAMES.items():
        signs_in_cat = [s for s in by_category.get(cat_id, [])]
        library["categories"].append({
            "id": cat_id,
            "name": cat_name,
            "count": len(signs_in_cat),
            "signs": [s["code"] for s in signs_in_cat],
        })

    # Summary
    total_with_questions = sum(1 for s in library["signs"].values() if s["questionIds"])
    print(f"Signs in catalog: {len(SIGN_CATALOG)}")
    print(f"Signs referenced in questions: {total_with_questions}")
    print(f"Signs with 0 question refs: {len(SIGN_CATALOG) - total_with_questions}")
    for cat_id, cat_name in CATEGORY_NAMES.items():
        count = len(by_category.get(cat_id, []))
        print(f"  {cat_name}: {count} signs")

    with open(OUTPUT, "w") as f:
        json.dump(library, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Saved → {OUTPUT}")
    return library


if __name__ == "__main__":
    build_library()
