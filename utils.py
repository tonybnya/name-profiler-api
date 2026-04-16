"""
Script Name : utils.py
Description : Helper functions
Author      : @tonybnya
"""

from uuid6 import uuid7


def generate_uuid_v7() -> str:
    return str(uuid7())
