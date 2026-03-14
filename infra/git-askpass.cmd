@echo off
REM Git ASKPASS helper - outputs PAT for https://github.com authentication
REM Called by git with a prompt string; we always return the token.
REM The URL stays clean; the token never appears in remote URLs or git log.
set PAT_FILE=G:\repos\AI\RoadTrip\ProjectSecrets\PAT.txt
set /p PAT=<%PAT_FILE%
echo %PAT%
