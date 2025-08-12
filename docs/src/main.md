# `main.py`

This is the main entry point of the application. It handles configuration loading, error catching, and invoking the alert pipeline.

---

## 🚀 Function: `main()`

Coordinates the execution of the alert system and handles failure gracefully.

### Steps Performed:
1. Loads configuration values from environment variables.
2. Calls `alerts_runner()` to trigger the full alert generation pipeline.
3. If the pipeline fails (`status_code != 200`), raises a `ValueError`.
4. Catches and logs any unhandled exceptions.
5. If credentials are missing, prints a specific error without sending an email.
6. Otherwise, sends an email to the administrator with details of the error.

---

## 🔐 Error Handling

- Checks for missing credentials (`GOOGLE_EMAIL` and `GOOGLE_PASS`) and prints a warning.
- On other exceptions, sends an alert email with the current exception message and system state.

---

## 📬 Uses

- [`config.load()`](config.md): Loads `.env` environment variables.
- [`alerts_runner()`](alerts_runner.md): Orchestrates the alert processing workflow.
- [`email_self()`](services/gmail.md): Sends error reports to admin via Gmail.
- [`state.logger`](global_state.md): Logs runtime information and errors.

---

## 🧪 Running the Program

```bash
python main.py
