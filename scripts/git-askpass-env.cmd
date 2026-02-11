@echo off
REM Git Credential Helper: Non-interactive password provider via environment variable
REM
REM This helper is called by git when it needs authentication credentials.
REM It reads the GitHub PAT from the GITHUB_TOKEN environment variable
REM and outputs it to stdout for git to consume.
REM
REM Used in conjunction with:
REM   GIT_ASKPASS=<这個腳本的路徑>
REM   GIT_TERMINAL_PROMPT=0
REM   GCM_INTERACTIVE=Never
REM   credential.helper=""
REM
REM Exit codes:
REM   0 = Successfully output token
REM   1 = Token not available in environment
REM
REM This ensures silent (non-interactive) authentication suitable for
REM agentic automation workflows.

setlocal ENABLEDELAYEDEXPANSION

REM If no token is set, fail so Git reports auth error
if "%GITHUB_TOKEN%"=="" exit /b 1

REM Output token only to stdout for Git to consume
echo %GITHUB_TOKEN%
exit /b 0
