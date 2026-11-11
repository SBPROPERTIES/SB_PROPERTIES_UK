# Advertising measurement

Implemented 11 November 2026. Pixel: TZqiQtfCoQV3xkSd8woaE3.

The repository contains static HTML published at sbproperties.uk. There is no build system, shared layout or checked-in Actions workflow. All 46 HTML pages include assets/measurement.js, assets/enquiry.js and assets/consent.css once. The 44 Formspree forms retain their original fields, validation and endpoint (mwpyrrke). There was no existing consent system or Pixel. Removed 34 unused placeholder N8N submission listeners; Formspree remains the delivery provider. No account-side spam settings have been changed.

Advertising is opt-in, with an always-available Cookie settings button. Consent is remembered in local storage; the ad code is stored only with consent in session storage. Withdrawal calls the documented Pixel consent API, removes queued lead calls and attribution cookies, and clears the ad code. No previous enquiry is replayed on acceptance or refresh. The Pixel loads and initializes once per page with debug disabled. No manually supplied customer identifiers are passed to the Pixel. Automatic advanced matching is disclosed in the banner and privacy policy.

Formspree AJAX uses FormData and Accept: application/json. A successful HTTP response is the only conversion callback. Pending and completed submissions are guarded. Pixel exceptions cannot prevent form delivery or change the success message. A denied or failed request displays an error and permits retry. HTML POST remains available without JavaScript.

The 404 legacy .html redirect retains the entire query string (including oppref and utm_content) and fragment. After consent the SDK handles the oppref cookie; the ad code survives navigation to another enquiry page in the same tab.

## Sources

- https://developers.openai.com/ads/measurement-pixel
- https://help.formspree.io/articles/building-your-form/submit-forms-with-javascript-ajax/

## Verification

Run node tests/measurement.cjs with Playwright installed (or NODE_PATH pointing to an existing installation) and Chrome available. The test suite intercepts every external request: no real Formspree submissions or OpenAI events are generated. It verifies all forms, success/failure/network errors, consent decline and withdrawal, withdrawal while pending, duplicate submits, blocked SDK, ad-code navigation, refresh, field preservation, minimal event payload, production Pixel configuration, redirect parameters, validation and mobile banner bounds.

Final owner checks: accept tracking, send an identifiable test enquiry, confirm delivery and Ad code in Formspree, and confirm lead_created in Ads Manager. Test actual ad attribution with an actual OpenAI ad click (a fabricated oppref is not valid attribution). Any account-side Formspree CAPTCHA challenge must also be checked in that real submission.

## Published enquiry pages

- /blog/empty-property-costs-glasgow/
- /blog/estate-agent-costs-vs-cash-buyer/
- /blog/estate-planning-glasgow/
- /blog/how-long-to-sell-house-glasgow/
- /blog/
- /blog/sell-house-fast-scotland/
- /blog/selling-inherited-property-scotland/
- /blog/selling-rental-property-glasgow/
- /blog/stop-house-repossession-scotland/
- /
- /privacy/
- /sell-house-fast-divorce-scotland/
- /sell-house-fast-needs-work-glasgow/
- /sell-house-fast-probate-scotland/
- /sell-house-fast-repossession-scotland/
- /sell-house-fast-tenanted-property-scotland/
- /sell-my-house-fast-ayrshire/
- /sell-my-house-fast-bearsden/
- /sell-my-house-fast-bishopbriggs/
- /sell-my-house-fast-cambuslang/
- /sell-my-house-fast-clydebank/
- /sell-my-house-fast-coatbridge/
- /sell-my-house-fast-dennistoun/
- /sell-my-house-fast-drumchapel/
- /sell-my-house-fast-dumbarton/
- /sell-my-house-fast-dumfries/
- /sell-my-house-fast-east-end-glasgow/
- /sell-my-house-fast-east-kilbride/
- /sell-my-house-fast-falkirk/
- /sell-my-house-fast-govan/
- /sell-my-house-fast-hamilton/
- /sell-my-house-fast-kirkintilloch/
- /sell-my-house-fast-maryhill/
- /sell-my-house-fast-motherwell/
- /sell-my-house-fast-paisley/
- /sell-my-house-fast-partick/
- /sell-my-house-fast-pollokshields/
- /sell-my-house-fast-possilpark/
- /sell-my-house-fast-rutherglen/
- /sell-my-house-fast-shettleston/
- /sell-my-house-fast-springburn/
- /sell-my-house-fast-stirling/
- /sell-my-house-fast-west-end-glasgow/
- /sell-my-house-fast-wishaw/
