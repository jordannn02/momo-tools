# Workflows

## 1. Build Your Capability Index

Start from `plugin/capabilities.example.json`.

Each capability should answer:

- What task should trigger it?
- What scope may it touch?
- What risks does it carry?
- Is it only visible, or verified?
- What caveats should the next agent see?

## 2. Route A Task

```bash
./plugin/scripts/momo-tools route --prompt "Review this repo for release risk"
```

Read the output:

- `matches`: likely capabilities;
- `gates`: risk boundaries triggered by the prompt;
- `blocked_by_prompt`: capabilities that matched but conflict with user limits.

## 3. Audit Your Router

Add representative prompts to `tests/fixtures/route-cases.json`.

```bash
./plugin/scripts/momo-tools audit
```

Use this for stable workflows you care about.

## 4. Pressure Test Conflicts

```bash
./plugin/scripts/momo-tools pressure
```

Pressure tests are deliberately awkward prompts. They protect boundaries such as:

- no-save vs. remember-this;
- no-web vs. latest/current;
- private-data vs. convenient connector;
- draft vs. send.

## 5. Install Locally

```bash
./scripts/install-local.sh
~/.momo-tools/bin/momo-tools dashboard
```

The installer creates a local copy only. It does not modify agent configs or
credential stores.

