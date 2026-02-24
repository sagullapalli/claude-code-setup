# Agent Boundaries (Mandatory)

**Three-tier system defining what agents can and cannot do autonomously.**

## Always Do (No Approval Needed)

- Run tests, linters, type checks
- Read files and explore codebase
- Follow project conventions and established patterns
- Check skills before technical work
- Update memory files at session end
- Use compression protocol when returning to orchestrator
- Plan with TodoWrite for non-trivial tasks

## Ask First (Human Approval Required)

- Delete files or directories
- Change architecture patterns or project structure
- Modify CI/CD pipelines or deployment config
- Add new dependencies or frameworks
- Make breaking API changes
- Destructive Git operations (force push, reset --hard, branch deletion)
- Scope changes beyond original request
- Create commits

## Never Do (Blocked)

- Push to main without explicit approval
- Delete or modify production data
- Expose secrets, credentials, or API keys in code/logs
- Bypass security checks or skip safety protocols
- Ignore test failures to "move faster"
- Implement without reading relevant files first
- Add features not explicitly requested
- Guess at API specs (always research first)
