#!/usr/bin/env python
import os
import sys
import subprocess
import argparse


def install_crawler(dev_mode=False):
    """Install the crawler module."""
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    crawler_dir = os.path.join(root_dir, "crawler")

    # Check if crawler directory exists
    if not os.path.isdir(crawler_dir):
        print(f"Crawler directory not found: {crawler_dir}")
        return False

    # Install requirements
    requirements_file = os.path.join(crawler_dir, "requirements.txt")
    if os.path.isfile(requirements_file):
        print(f"Installing crawler requirements from {requirements_file}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])

    # Install crawler module
    print(f"Installing crawler module from {crawler_dir}")

    # Use development mode if requested
    if dev_mode:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", crawler_dir])
        print(f"Crawler module installed in development mode")
    else:
        subprocess.check_call([sys.executable, "-m", "pip", "install", crawler_dir])
        print(f"Crawler module installed")

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Install the crawler module")
    parser.add_argument("--dev", action="store_true", help="Install in development mode")
    args = parser.parse_args()

    if install_crawler(args.dev):
        print("Installation successful")
    else:
        print("Installation failed")
        sys.exit(1)