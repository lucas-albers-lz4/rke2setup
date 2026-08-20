# Changelog

## [Unreleased]
### Fixed
- Consolidate RKE2 cleanup into one role path; keep confirmation on the playbook so extra-destructive leftover cleanup cannot run without it.
- Cleanup process kill skips the Ansible task shell; path removal always runs after leftover cleanup; host journal files are not vacuumed.

## [1.0.0] - YYYY-MM-DD
### Added
- Initial release
- Six-node cluster deployment support
- Comprehensive validation
- Automated cleanup
