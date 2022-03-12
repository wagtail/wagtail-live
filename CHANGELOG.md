# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- Fix: Set content-type to 'plain/text' as expected by Slack API on url verification
- Gracefully handle error when deleting a message that is no longer present on a live page
- Add ability for publishers to use secure WebSocket connections.
- Added `WAGTAIL_LIVE_POST_BLOCK` setting to extend/customize the base `LivePostBlock` class.
- Added `process_livepost_before_add` hook to perform additional processing on a live-post before it's added.

## [1.0.0] - 2021-10-28

- Initial release
