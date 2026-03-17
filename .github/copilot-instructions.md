# RoadTrip Copilot Instructions

## Critical Command Safety (Windows + PowerShell)

- Always assume this repository runs on Windows unless the prompt explicitly says otherwise.
- Always assume this machine is Windows 11 unless the prompt explicitly says otherwise.
- Use `py` for Python execution commands.
- Use `py -m pip install ...` for package install commands.
- Do not suggest bare `python ...` or bare `pip install ...` commands for this workspace.
- Prefer PowerShell-friendly commands and path separators for runnable examples.

## PPA Execution Boundary

- RoadTrip is the developer workspace and planning surface.
- The executable agentic application is `G:\repos\AI\PPA`.
- Any `dotnet run`, `dotnet build`, `dotnet test`, or solution/project discovery for the PPA must target `G:\repos\AI\PPA`, not RoadTrip.
- For .NET 10 project structure in this environment, prefer `.slnx` solution files. Do not assume an older `.sln` file exists.
- Do not treat RoadTrip as the runtime host for orchestrator, executor, triage, evaluator, tester, or agent-factory responsibilities. If a dev instance exists in RoadTrip, it is only a temporary development surface destined for the separate PPA app.

## RoadTrip Mistake-Prevention Reminder (Always Apply)

Before returning runnable commands, do a quick command-safety check:

1. Replace `python` with `py` for command examples.
2. Replace `pip install` with `py -m pip install`.
3. Ensure RoadTrip aliases (`gpush`, `gpush-dry`, `gpush-log`) are only suggested when current directory is RoadTrip.
4. If relevant to git push automation, remind user to verify `$env:GITHUB_TOKEN`.

## Documentation References

- Read and follow [COMMON_MISTAKES.md](../COMMON_MISTAKES.md) for prevention patterns.
- Read and follow [CLAUDE.md](../CLAUDE.md) for critical reminders and project conventions.

## Scope Discipline

- Keep fixes focused on the requested task.
- Avoid unrelated refactors.
- Preserve existing style and conventions.
