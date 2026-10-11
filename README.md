# SB Properties website

Static HTML, CSS and JavaScript. The HTML files are the current editable source; no framework installation is required.

## Preview

From this directory run `python -m http.server 8081 --bind 127.0.0.1` and open `http://127.0.0.1:8081/`. Root-relative links require an HTTP server.

## Validate

Run `python tools/check_conversion_site.py` for links/assets, headings, labels, schema syntax and preservation of the original form/webhook delivery contract. Run `python tools/audit_technical_seo.py` for crawl depth, metadata, fragments, asset sizes and location-content similarity. JSON syntax checks do not replace Google's Rich Results Test on the deployed pages.

Check changed JavaScript with `node --check assets/conversion.js`, `node --check assets/guides.js` and `node --check assets/analytics.js`. Browser-check the guide filters, empty-search reset, mobile navigation, calculator and enquiry layout. Do not submit test leads to production unless explicitly requested. Analytics loads only on the production hostnames, so local preview interactions do not enter GA4.

## Prepare a public release

Run `python tools/build_public_site.py` to check the public file inventory. Use `python tools/build_public_site.py --build` to prepare `dist/` containing only sitemap pages, the error page, discovery files and referenced assets. This command does not publish anything. The build verifies output paths and only removes obsolete files from its own previous manifest.

Do not manually copy files into `dist/`. The build rejects unexpected files so an old export or backup cannot silently enter a later release.

`dist/` is intended for an artifact-based static deployment. For a GitHub Pages branch/Jekyll build, `_config.yml` excludes internal source/data files. Confirm the actual hosting build mode before publication. Apache `.htaccess` and Netlify `_redirects` rules are not executed by GitHub Pages.

Never upload Search-Data, research reports, logs, temporary files or Python maintenance scripts as public site content. After publication, confirm those paths return 404 and validate real canonical/404/crawler responses.

## Editing notes

The `build_*`, `refine_*`, `fix_*`, `polish_*`, `final*` and `improve_search_discovery.py` files include one-off migration scripts. Do not run them as a general build: they can overwrite later editorial changes. `build_public_site.py` is the release packaging command; it copies the current HTML rather than regenerating it.

Lead forms continue to POST to their existing Formspree action. Original secondary webhook handlers are preserved because the owner confirmed delivery. Analytics submit attempts are not confirmed successful enquiries. Shared events omit form values and search text.

Research and verification notes are kept locally in `research/`, which is excluded from new Git commits and site publication. They include the limits of the supplied GSC/GA exports and outstanding needs for genuine business evidence and live account checks.
