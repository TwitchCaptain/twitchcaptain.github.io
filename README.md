# twitchcaptain.com

Static site for the [TwitchCaptain](https://github.com/TwitchCaptain) GitHub organization.

## What it does

- Lists public, non-fork, non-archived org repositories
- Shows each repo description from GitHub
- Links to GitHub Pages project sites when `has_pages` is enabled (for example [`/hangman/`](https://twitchcaptain.com/hangman/))
- Refreshes `projects.json` on a daily GitHub Actions schedule

## Local sync

```bash
python3 scripts/sync_projects.py
```

Optional: set `GITHUB_TOKEN` / `GH_TOKEN` for authenticated API calls.

## Deploy

Pushes to `main` run [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) and publish to GitHub Pages with the `twitchcaptain.com` CNAME.
