"""
Script Name : utils.py
Description : Helper functions
Author      : @tonybnya
"""

from uuid6 import uuid7


def generate_uuid_v7() -> str:
    return str(uuid7())


def classify_age(age: int) -> str:
    if age <= 12:
        return "child"
    elif age <= 19:
        return "teenager"
    elif age <= 59:
        return "adult"
    return "senior"
