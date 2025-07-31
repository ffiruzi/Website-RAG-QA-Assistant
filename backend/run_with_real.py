#!/usr/bin/env python
import sys
import os
import uvicorn

# Get absolute paths
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(backend_dir)

# Add project root to Python path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print(f"Backend directory: {backend_dir}")
print(f"Project root: {project_root}")
print(f"Python path: {sys.path}")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)