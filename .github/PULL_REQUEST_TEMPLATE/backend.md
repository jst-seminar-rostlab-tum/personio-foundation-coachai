## 🔍 Current Situation

Link resolved issues with `#`.
What was the state of the backend before this PR? What problem are you solving?

## 💡 Proposed Solution

What architectural/code changes did you make?
Include:

- Important design decisions.
- Code snippets (if relevant).
- Usage examples (e.g. for new libraries, background jobs).
- Screenshots (only if there’s a UI change like Swagger updates).

## 🚨 Implications

- Does this affect any APIs (add/remove/change endpoints)?
- Do other systems or teams depend on this behavior?
- Is there another PR (frontend or backend) that must be merged first?
- Did you deprecate/remove any feature or behavior?

## ✅ Local Testing Instructions

How can someone test your changes locally?
Please include:

- Any required environment variables.
- Sample curl/Postman requests.
- Steps to run test cases (if manual/integration testing is needed).

## 🔬 Developer Checklist (must complete before marking PR as **Ready for Review**)

> Keep the PR as a **draft** until all of the following are checked and you're confident it's ready for review.

- [ ] I tested the app locally using `uv run fastapi dev` or equivalent.
- [ ] I ran `docker compose down -v` to removing all volumes and then `docker compose up --build` to build and start the app.
- [ ] I confirmed that all new or changed **environment variables** are:

  - [ ] The app has been tested with the new environment variables removed (e.g. deleted from .env, app started in a fresh terminal).
  - [ ] Documented clearly in `.env.example` or a config file.
  - [ ] Defaulted sensibly (or fail-fast if truly required).
  - [ ] Communicated to other stakeholders (if needed).

- [ ] All migrations or DB changes have been tested locally.
- [ ] I added or updated relevant unit/integration tests.
- [ ] I included clear **testing instructions** in this PR.
- [ ] I have considered performance, logging, and error handling.

## 🧠 Reviewer Notes

- Which parts of the code need extra attention?
- Is this a functional change, a refactor, or a cleanup?
- Any known issues or follow-up work?
