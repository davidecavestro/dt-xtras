---
trigger: glob
globs: **/*(.vue|.js|.py)
---

# Never catch exceptions unless explicitly prompted or confirmed
# Always use a logging system instead of raw System.out (no console.log, no print, no println)
# Always check DT openapi at /workspace/docs/dt-openapi.json for backend api implementations
# Be conservative: limit changes to just the needed ones, unless prompted otherwise
# Don't operate partial reads on files: read and validate the entire source file before making any changes
# When you insert new code, check that you are not duplicating variables, functions or code blocks
# When you remove code, check that you are not removing needed imports or functions
# For frontend, always wrap http calls into stores
