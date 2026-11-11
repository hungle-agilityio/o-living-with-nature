# Django and Python rules

- Every function and method has type hints; `mypy --strict` with the Django plugin passes.
- No `*` imports; explicit imports only.
- No business logic in views, templates, models or signals; it lives in a service and is called explicitly.
- Any list that touches the database uses `select_related` or `prefetch_related`; an N+1 query blocks the pull request.
- Input from visitors (a later form, a query parameter) is validated by a Django form before use.
- Never log personal data (a visitor's name, phone, email) or a secret.
- Tests: `pytest` with `pytest-django` and `pytest-mock`, in `src/<feature>/tests/` beside the code; services aim for 90 percent coverage; never call the network in a test.
- Settings read from the environment; development defaults are safe and never used in production (`DJANGO_DEBUG=0` needs `DJANGO_SECRET_KEY`).
