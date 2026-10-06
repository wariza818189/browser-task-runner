# Contributor instructions

- Use Python 3.12+ and the existing external virtual environment. In this workspace
  it is `../browser-task-runner-venv`; do not create a repo-local `.venv`.
- Use synchronous Playwright with Chromium and pytest. Keep dependencies minimal.
- Keep CLI orchestration, browser lifecycle, workflow steps, screenshots,
  extraction, and report generation separate, with explicit inputs and outputs.
- V1 supports one deterministic Sauce Demo workflow only. Follow `WORKFLOW.md`.
- The foundation milestone is launch/close only: do not add navigation, login,
  interactions, screenshots, extraction, or report writing until the next milestone.
- Automate only public/demo pages or pages the user is authorized to use. Never
  bypass authentication, CAPTCHAs, paywalls, anti-bot controls, or access restrictions.
  Stop on an unexpected access barrier; do not add evasion or retry-to-bypass logic.
- Do not add cloud deployment, databases, scheduling, or AI features.
- Use reliable browser cleanup, explicit timeouts, and Playwright locator waits
  when workflows are implemented. Avoid arbitrary sleeps and global browser state.
- Test pure extraction/report logic separately from browser integration when those
  modules are implemented. The current smoke test must use real Chromium and fail
  visibly if browser setup is unavailable.
- Keep generated artifacts, credentials, and virtual environments out of Git.
- Run dependency/import checks where possible, `python -m pytest`,
  `git diff --check`, and `git status --short`. Record results and blockers in
  `PROJECT_STATUS.md`; do not claim checks passed unless they ran successfully.
- Do not commit or push unless the user explicitly requests it.
