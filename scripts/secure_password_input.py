#!/usr/bin/env python
"""
Secure password input module for Windows environments.
This module provides a secure way to input passwords in Windows environments,
ensuring that the password is not displayed on the screen.
"""

import sys
import ctypes
from ctypes import wintypes
import msvcrt

def secure_getpass(prompt='Password: '):
    """
    A secure password input function for Windows that ensures the password
    is not displayed on the screen.

    Args:
        prompt (str): The prompt to display to the user

    Returns:
        str: The password entered by the user
    """
    # Print the prompt
    sys.stdout.write(prompt)
    sys.stdout.flush()

    password = ""
    while True:
        # Read a single character without echoing
        char = msvcrt.getch()

        # Convert from bytes to string if needed
        if isinstance(char, bytes):
            char = char.decode('utf-8')

        # Check for Enter key (end of input)
        if char == '\r' or char == '\n':
            sys.stdout.write('\n')
            return password

        # Check for backspace
        if char == '\b' or ord(char) == 8:
            if password:
                # Remove the last character from the password
                password = password[:-1]
                # Erase the last * from the screen
                sys.stdout.write('\b \b')
                sys.stdout.flush()
        # Ignore control characters
        elif ord(char) < 32:
            continue
        else:
            # Add the character to the password
            password += char
            # Print a * to the screen
            sys.stdout.write('*')
            sys.stdout.flush()

def get_password(prompt='Enter your password: '):
    """
    Get a password securely, ensuring it's not displayed on the screen.
    This function will use the secure_getpass function on Windows.

    Args:
        prompt (str): The prompt to display to the user

    Returns:
        str: The password entered by the user
    """
    return secure_getpass(prompt)

if __name__ == "__main__":
    # Test the function
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
    else:
        prompt = "Enter password: "

    password = get_password(prompt)
    print(f"You entered: {'*' * len(password)}")
