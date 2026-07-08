# MoMo_tools Evidence Dashboard

This static demo turns the development-time screenshots in `workspace-outputs/` into a public-safe visual evidence layer.

Open locally:

```bash
python3 -m http.server 4173 --directory demo
```

Then visit `http://127.0.0.1:4173`.

Regenerate the vector evidence assets:

```bash
node demo/generate-assets.mjs
```

The demo is intentionally static and synthetic:

- no private connectors;
- no production data;
- no account screenshots;
- no runtime writes;
- no network calls.
