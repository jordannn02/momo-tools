# Security Policy

MoMo_tools is a local-first capability router. It should not require secrets,
tokens, cookies, browser profiles, or production credentials to run its core
validation, routing, audit, or pressure tests.

## What To Report

Please report issues that could cause:

- secrets or local paths to be written into shared reports;
- private capabilities to be promoted without evidence;
- destructive tools to be recommended without an approval gate;
- external services to be called during local-only validation;
- route results to ignore explicit no-write, no-web, or no-save constraints.

## Safe Defaults

The public package ships with synthetic examples only. Do not publish your real
`capabilities.local.json`, private connector names, internal hostnames, customer
names, screenshots, account data, or workflow evidence.

## Before Publishing A Fork

Run:

```bash
./plugin/scripts/momo-tools test
rg -n "secret|token|api_key|password|HOME_PATH|WINDOWS_PATH|internal|customer" .
```

Review every match manually. Some words such as `secret` can appear in security
documentation; the goal is to prevent real secrets and private environment
details from leaking.
