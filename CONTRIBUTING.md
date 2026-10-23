# Contributing

1. Run locally with `python app.py` and reproduce the behavior to change.
2. Create a branch and make a focused change.
3. Add an integration test when changing API or database behavior.
4. Run `python -m unittest -v test_app`.
5. For frontend changes, check `node --check static/app.js` and inspect the app
   in a browser at desktop and mobile sizes.
6. Regenerate the static demo with `python scripts/build_demo.py` and review the
   generated diff. Never export real student information.
7. Update relevant documentation and open a pull request with a concise problem,
   behavior change and validation description.

Potential next issues: authenticated student access, schema migrations, teacher
grade management and a PostgreSQL adapter. These are ideas, not implemented work.
