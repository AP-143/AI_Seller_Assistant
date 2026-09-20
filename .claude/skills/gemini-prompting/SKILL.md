---
name: gemini-prompting
description: Prompt patterns for this repo's Gemini calls (services/gemini_client.py, graph/nodes.py) — product photo editing and marketplace text generation. Use when writing or editing any prompt sent to Gemini in this project, or when output quality/reliability from a Gemini call regresses.
---

# Gemini prompting patterns for this repo

Researched patterns, applied in `services/gemini_client.py` and `graph/nodes.py`.
Reuse these instead of re-deriving from scratch.

## Image editing (`generate_product_photo`, model `gemini-2.5-flash-image`)

Source: [official Gemini image-gen docs](https://ai.google.dev/gemini-api/docs/image-generation),
[Nano Banana prompt patterns](https://www.promptzone.com/darcy_reddy/nano-banana-prompt-patterns-for-gemini-25-flash-image-447f).

Gemini image models take instructions like a person, not a diffusion UI: full
sentences and spatial relations, not comma-separated tags.

- **Freeze clause**: state explicitly what must NOT change — "keeping the
  product's shape, color, material, and logo exactly the same" beats vague
  wording like "don't change much". Vague freeze clauses get ignored more often.
- **Role + goal, not a fixed checklist**: an earlier version of this prompt
  hardcoded one visual template (white background, three-point softbox, 1:1
  crop) for every product. User feedback: that's no different from typing a
  static prompt into Gemini by hand — it defeats the point of running this as
  a system. Fixed the prompt to frame the model as "a professional product
  photo editor" and state the goal (upload-ready marketplace photo) plus
  product context (name + category), then let the model choose background,
  lighting, angle, and composition itself — the same judgment call a real
  photographer makes per product type, not one template for everything. A
  fixed template ("three-point softbox", "pure white background") is still a
  valid Google-documented pattern for a single deliberately fixed style — use
  it only when the user actually wants that literal fixed look, not as the
  default.
- **What actually changed output quality when tested on this project**:
  - `gemini-2.5-flash-image` kept product fidelity better than
    `gemini-3.1-flash-image` and `gemini-3-pro-image` in real testing, despite
    being the cheapest and the oldest of the three. Don't assume newer/pricier
    = better fidelity — re-test empirically before switching models.
  - `gemini-2.5-flash-image` is DEPRECATED 2026-10-02. When it's pulled,
    re-run this same empirical fidelity comparison across whatever models are
    current — don't just pick the newest by default.
- **Multiple variants**: `candidate_count` in the request config is REJECTED
  for this model ("Multiple candidates is not enabled for this model", 400).
  To get N image variants, issue N separate `generate_content` calls (see
  `generate_product_photos` — parallelized with `ThreadPoolExecutor`), not
  one call with `candidate_count=N`. This costs N× the per-image price.

## Structured text generation (`generate_json`, model in `MODEL`)

Source: [Gemini prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies).

For any output with a fixed shape (title/description/price, N captions, etc.),
use `response_mime_type: "application/json"` + `response_schema` (see
`gemini_client.generate_json`) instead of asking the model to emit marker text
(`JUDUL:`/`DESKRIPSI:`) and parsing it with string splits.

- Manual marker parsing is fragile: it breaks on model phrasing drift, extra
  whitespace, or the model echoing a marker word inside its own content.
  Structured output removes that failure class entirely — the SDK returns
  already-valid JSON per the schema.
- Keep schema field `description`s short and specific (max length, tone,
  format expectations) — they do real prompting work, not just documentation.
- Don't over-nest the schema. Flat fields (`title`, `description`,
  `price_range`) parse more reliably than nested objects for this model size.
- **`max_output_tokens` gotcha**: `MODEL` (`gemini-3.6-flash`) spends part of
  the token budget on hidden reasoning tokens before writing the visible JSON
  — a real test showed 615 total tokens for an 85-token JSON body. A budget
  that looks generous for the JSON alone (e.g. 800) can still truncate mid-
  string and raise `JSONDecodeError: Unterminated string`. Use a generous
  budget (2048+) for anything schema-shaped on this model, not just enough
  for the expected JSON length. `generate_json` now raises a clear
  `RuntimeError` on `FinishReason.MAX_TOKENS` instead of leaving you to debug
  a JSON parse error.

## When NOT to use structured output

Free-form generation with no fixed shape (e.g. a single prose answer) doesn't
need a schema — plain `generate()` is fine. Only reach for `generate_json`
when the caller needs to pull out named fields.
