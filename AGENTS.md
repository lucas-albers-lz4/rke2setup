# AGENTS.md — rke2setup

RKE2 cluster bootstrap via Ansible. Core flow: `make lint` / `make deploy`
(see [CONTRIBUTING.md](CONTRIBUTING.md)).

## CodeRabbit (review bot)

Draft PRs are **not automatically** reviewed by CodeRabbit (repo default);
manual `@coderabbitai review` can still trigger on drafts. Review limits are
**plan-specific** (e.g. Free 1/hr, Pro 5/hr, Pro+ 10/hr — check remaining
quota with `@coderabbitai rate limit`), not a fixed ~3/hr cap. Marking Ready
makes the PR *eligible* for automatic review. CodeRabbit takes ~5–10 min to
write a round; **wait for the round to complete before pushing fixes** (new
`COMMENTED` submission from `coderabbitai[bot]` with `commit_id` = your head;
a rate-limit comment means the head was NOT reviewed), batch all fixes into
one push, and never declare the gate green while a round is still in flight.
Full protocol: [docs/CODERABBIT.md](docs/CODERABBIT.md).
