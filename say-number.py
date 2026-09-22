#!/usr/bin/env python3
"""say-number: Arabic non-negative integers → Traditional Chinese reading (繁體中文唸法).

Usage:
  python3 say-number.py <number>
  python3 say-number.py --test
"""

from __future__ import annotations

import sys

DIGITS = "零一二三四五六七八九"
MIN_N = 0
MAX_N = 99_999_999


def _coeff(d: int, unit: str) -> str:
    """Digit as coefficient of unit. 二→兩 for 百/千/萬; keep 二 for 十 and bare."""
    if d == 2 and unit in ("百", "千", "萬"):
        return "兩"
    return DIGITS[d]


def say_section(n: int, short_teens: bool = True) -> str:
    """Convert 0..9999 to Traditional Chinese. Empty string for 0.

    When short_teens is False, 10–19 always use 一十… (never bare 十),
    e.g. after a wan→rest bridge 零 so 10010 → 一萬零一十 not 一萬零十.
    """
    if n == 0:
        return ""
    if n < 0 or n > 9999:
        raise ValueError(f"section out of range: {n}")

    qian = n // 1000
    bai = (n % 1000) // 100
    shi = (n % 100) // 10
    ge = n % 10

    parts: list[str] = []
    pending_ling = False

    def emit_ling_if_needed() -> None:
        nonlocal pending_ling
        if pending_ling:
            parts.append("零")
            pending_ling = False

    if qian:
        parts.append(_coeff(qian, "千") + "千")

    if bai:
        emit_ling_if_needed()
        parts.append(_coeff(bai, "百") + "百")
    elif qian:
        pending_ling = True

    if shi:
        emit_ling_if_needed()
        # Teens at start of section with no 千/百: 十/十一 not 一十/一十一
        # unless short_teens=False (e.g. after wan bridge 零 → 零一十)
        if shi == 1 and qian == 0 and bai == 0 and short_teens:
            parts.append("十")
        else:
            parts.append(_coeff(shi, "十") + "十")
    elif (qian or bai) and ge:
        pending_ling = True

    if ge:
        emit_ling_if_needed()
        parts.append(DIGITS[ge])

    return "".join(parts)


def say_number(n: int) -> str:
    """Convert 0..99999999 to Traditional Chinese reading."""
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("n must be int")
    if n < MIN_N or n > MAX_N:
        raise ValueError(f"number out of range [{MIN_N}, {MAX_N}]: {n}")

    if n == 0:
        return "零"

    wan = n // 10000
    rest = n % 10000
    parts: list[str] = []

    if wan:
        if wan == 2:
            # bare 二 as coefficient of 萬 → 兩
            parts.append("兩萬")
        else:
            parts.append(say_section(wan) + "萬")

    if rest:
        if wan and rest < 1000:
            parts.append("零")
            parts.append(say_section(rest, short_teens=False))
        else:
            parts.append(say_section(rest))

    return "".join(parts)


def run_tests() -> int:
    cases = [
        (0, "零"),
        (1, "一"),
        (2, "二"),
        (10, "十"),
        (11, "十一"),
        (12, "十二"),
        (20, "二十"),
        (21, "二十一"),
        (100, "一百"),
        (110, "一百一十"),
        (111, "一百一十一"),
        (200, "兩百"),
        (1000, "一千"),
        (1001, "一千零一"),
        (1010, "一千零一十"),
        (1011, "一千零一十一"),
        (1100, "一千一百"),
        (1110, "一千一百一十"),
        (2000, "兩千"),
        (2001, "兩千零一"),
        (10000, "一萬"),
        (10001, "一萬零一"),
        (10010, "一萬零一十"),
        (10011, "一萬零一十一"),
        (10100, "一萬零一百"),
        (11000, "一萬一千"),
        (11100, "一萬一千一百"),
        (20000, "兩萬"),
        (20001, "兩萬零一"),
        (22000, "兩萬兩千"),
        (100000, "十萬"),
        (100001, "十萬零一"),
        (100010, "十萬零一十"),
        (101000, "十萬一千"),
        (110000, "十一萬"),
        (200000, "二十萬"),
        (2000000, "兩百萬"),
        (20000000, "兩千萬"),
        (12345678, "一千兩百三十四萬五千六百七十八"),
        (99999999, "九千九百九十九萬九千九百九十九"),
        (10000001, "一千萬零一"),
        (10001000, "一千萬一千"),
        (10000100, "一千萬零一百"),
    ]

    failed = 0
    for n, expected in cases:
        got = say_number(n)
        if got != expected:
            print(f"FAIL  {n} → got {got!r}, expected {expected!r}")
            failed += 1
        else:
            print(f"PASS  {n} → {got}")

    total = len(cases)
    passed = total - failed
    print()
    if failed == 0:
        print(f"PASS summary: {passed}/{total} tests passed")
        return 0
    print(f"FAIL summary: {passed}/{total} passed, {failed} failed")
    return 1


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(
            "Usage: python3 say-number.py <number>\n"
            "       python3 say-number.py --test",
            file=sys.stderr,
        )
        return 2

    arg = argv[1]
    if arg == "--test":
        return run_tests()

    try:
        n = int(arg, 10)
    except ValueError:
        print(f"error: not an integer: {arg!r}", file=sys.stderr)
        return 2

    if n < MIN_N or n > MAX_N:
        print(
            f"error: number must be in [{MIN_N}, {MAX_N}], got {n}",
            file=sys.stderr,
        )
        return 2

    print(say_number(n))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
