# OS Command Injection: In-Band Output

**Variant 1.** A Flask ping diagnostic demonstrates command injection by returning the injected command's output in the HTTP response. See the [group README](../README.md) for team ownership.

## Run locally

Requires Python 3 with `venv` and `pip`, Bash, and the system `ping` executable. Use Linux, WSL, or macOS: the application calls `ping -c 2`, which is incompatible with native Windows `ping`.

From the repository root:

```bash
cd os-command-injection-variant_1
bash run.sh
```

The [launcher](run.sh) creates `.venv` and installs [requirements.txt](requirements.txt) on first run. Open http://127.0.0.1:5000. Switch between **Vulnerable** and **Mitigated** in the dashboard; no server restart is needed.

## Vulnerable implementation and root cause (a, c)

In [`app.py`](app.py), `POST /api/ping` accepts `target` and `mode`. The `vulnerable` branch interpolates the target into a shell command:

```python
command = f"ping -c 2 {target}"
process = subprocess.run(
    command, shell=True, capture_output=True, text=True, timeout=6
)
output = process.stdout + process.stderr
```

User input becomes shell syntax: a semicolon ends the ping command and starts another command with the application's privileges. Both stdout and stderr are returned in the JSON `output` field, making this an in-band variant.

## Exploit and verification (b, d)

For a detailed terminal demonstration, follow the [manual curl walkthrough](WALKTHROUGH.md).

Use the dashboard to perform these steps:

1. Select **Vulnerable**, submit `127.0.0.1`, and confirm that ping output appears.
2. Submit the exact payload `127.0.0.1; whoami`. The expected response is HTTP 200 with `status: "success"`; the output includes the username running the application.
3. Select **Mitigated** and resubmit `127.0.0.1; whoami`. Expect HTTP 400 with `status: "blocked"` and `executed_command: null`. The request is rejected before subprocess execution.
4. Submit the benign target `127.0.0.1` again in **Mitigated** mode to confirm normal diagnostics still work.

Capture the actual command output and a screenshot of the blocked attempt for the submission. The username and ping timings depend on the local environment.

## Implemented mitigation (d)

The `mitigated` branch in [`app.py`](app.py) applies two controls:

- **Character allow-list:** `r"^[a-zA-Z0-9.-]+$"` rejects spaces and shell metacharacters before execution.
- **Argument-vector execution:** passes the executable and arguments separately with `shell=False`, so the shell does not interpret the target.

```python
cmd_args = ["ping", "-c", "2", target]
process = subprocess.run(
    cmd_args, shell=False, capture_output=True, text=True, timeout=6
)
```

The allow-list blocks the demonstrated payload; avoiding shell interpretation also prevents shell metacharacters from becoming extra commands.

## Other mitigations (e)

A native networking library can replace external command execution, removing this shell-command construction entirely. Running the service with a dedicated, minimally privileged account limits the impact of a compromise. These complement the allow-list validation and argument-vector execution already implemented.
