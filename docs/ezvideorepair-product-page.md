# EZVideoRepair product pages

Local-only pages: `ezvideorepair.html` (Chinese primary) and `ezvideorepair_en.html` (English). Existing personal index pages are unchanged.

Edit paired content in `content/ezvideorepair/zh.json` and `en.json`, shared structure in `templates/ezvideorepair/page.html`, and styles/scripts in `assets/products/ezvideorepair/`.

Run `python3 scripts/build_ezvideorepair.py` to regenerate both pages and `python3 -m unittest discover -s tests -p test_ezvideorepair.py` to check structural parity, assets and links. Run the existing `python3 scripts/maintain.py check` separately for personal content. For visual verification, check both languages at desktop and narrow mobile widths, including FAQ keyboard interaction.

Screenshots are the application's actual no-media interface, not a fabricated restoration comparison. Source and model CTAs point to GitHub and Hugging Face. There is no public installer/App Store URL configured. Do not publish the site or add unsupported 4K/8K/interpolation claims without a verified product change.
