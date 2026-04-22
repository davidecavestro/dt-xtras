---
trigger: glob
globs: **/*(.vue|.js|.py)
---

# Never catch exceptions unless explicitly prompted or confirmed: prefer failing fast
# Always use a logging system instead of raw System.out (no console.log, no print, no println)
# Always check DT openapi at /workspace/docs/dt-openapi.json for backend api implementations
# Be conservative: limit changes to just the needed ones, unless prompted otherwise
# Don't operate partial reads on files: read and validate the entire source file before making any changes
# When you insert new code, check that you are not duplicating variables, functions or code blocks
# When you remove code, check that you are not removing needed imports or functions
# For frontend, always wrap http calls into stores
# Our application is made of frontend and backend: the frontend is a Vue.js application and the backend is a Python application
# When you work on the backend, always check the Dependency-Track api available at /workspace/docs/dt-openapi.json
# The Backend implements it's own api calling Dependency-Track under the hoods but also wraps Dependency-Track api when no additional logic is needed
# The frontend should only consume the Backend api, never call Dependency-Track directly
# The backend state is a local yaml file with taxonomies: all other data is persisted by Dependency-Track and the backend only exposes the data through it's own api
# Never hardcode logic tied to specific tag names or currently defined taxonomies: it's dynamic data
# When you need to access the backend during development, bu convention you can retrieve the auth token with `curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"username": "admin", "password": "password"}'` then use it on subsequent calls as header `Authorization: Bearer ...`
# The backend is splitted into separated into multiple fiels for separation of concerns: keep responsibilities separated
# For regex always use `regexpp` at frontend and `regex` at backend
# Never directly edit `taxonomies.yaml`: it's data and you don't have to "fix" it
