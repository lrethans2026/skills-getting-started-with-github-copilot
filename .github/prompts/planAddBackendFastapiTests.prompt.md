## Plan: Add Backend FastAPI Tests

Add route-level backend tests under a new top-level `tests/` package, using `pytest` plus FastAPI's test client pattern against the existing app in `src/app.py`. Structure each test with the AAA (Arrange, Act, Assert) pattern so setup, request execution, and assertions stay visually separated and easy to scan. Add `pytest` to `requirements.txt` so the backend suite can run in a freshly installed environment. Keep the application structure unchanged and isolate tests with fixtures that snapshot and restore the in-memory `activities` store between tests.

**Steps**
1. Add `pytest` to `requirements.txt` so the backend test tooling is installed with the rest of the project dependencies.
2. Create the top-level test layout: `tests/` plus an optional shared fixture module or `conftest.py` for reusable client and state-reset fixtures.
3. Add a `client` fixture that imports `app` from `src.app` and provides a test client for endpoint-level tests. This is independent of most assertions but blocks all route tests.
4. Add a function-scoped fixture that deep-copies `src.app.activities` before each test and restores it afterward so signup and unregister tests cannot leak state across cases. This depends on step 2 and should be implemented before most mutating tests.
5. Add read-only endpoint coverage for `GET /activities`, including a status-code check, response-shape assertions, and a sanity check that the seeded activities collection is returned, with each test written in explicit Arrange, Act, and Assert sections. This depends on step 3.
6. Add signup endpoint coverage for `POST /activities/{activity_name}/signup`, including success, duplicate signup rejection, and unknown-activity rejection, with each case following the AAA structure. This depends on steps 3 and 4.
7. Add unregister endpoint coverage for `DELETE /activities/{activity_name}/signup`, including success, not-signed-up rejection, and unknown-activity rejection, with each case following the AAA structure. This depends on steps 3 and 4 and can run in parallel with step 6 once fixtures exist.
8. Verify the tests with `pytest` scoped to the new backend suite and adjust any fixture/import issues exposed by the first run. This depends on steps 5 through 7.
9. Optionally tighten `pytest.ini` only if discovery/import behavior needs it; otherwise leave the existing config as-is to keep the change minimal. This depends on step 8.

**Relevant files**
- `/workspaces/skills-getting-started-with-github-copilot/src/app.py` — existing FastAPI app, global `activities` store, and route functions `get_activities`, `signup_for_activity`, and `unregister_from_activity` that the tests will exercise.
- `/workspaces/skills-getting-started-with-github-copilot/pytest.ini` — current pytest configuration (`pythonpath = .`), likely sufficient for importing `src.app` from a separate `tests/` directory.
- `/workspaces/skills-getting-started-with-github-copilot/requirements.txt` — dependency list, now including `pytest`, so the backend test suite can run after a standard install.
- `/workspaces/skills-getting-started-with-github-copilot/tests/conftest.py` — recommended location for shared `TestClient` and activity-reset fixtures.
- `/workspaces/skills-getting-started-with-github-copilot/tests/test_activities.py` — recommended location for route-level backend tests covering the three current endpoints.

**Verification**
1. Run `pytest tests/test_activities.py` to validate the new backend test file in isolation.
2. Run `pytest` to confirm the separate `tests/` directory is discovered correctly by the repo-wide test command.
3. Manually confirm mutating tests are order-independent by ensuring repeated `pytest` runs pass without residual participant changes.

**Decisions**
- Use a separate top-level `tests/` directory rather than colocating tests under `src/`.
- Keep production code changes minimal; prefer pytest fixtures over introducing an app factory or service-layer refactor, and structure the tests themselves with clear AAA sections.
- Scope this work to backend FastAPI route tests only; frontend static assets and browser behavior are excluded.
- Do not add capacity or email-format tests yet, because the current application does not implement those behaviors and the task is test addition rather than feature expansion.

**Further Considerations**
1. If the team later wants cleaner isolation or more scalable tests, a follow-up refactor can extract the in-memory store behind a dependency or app factory without blocking the initial backend suite.
2. If the team later splits runtime and development dependencies, move `pytest` into a dedicated development requirements file or project metadata, but keep it in `requirements.txt` for now to match the current setup.
