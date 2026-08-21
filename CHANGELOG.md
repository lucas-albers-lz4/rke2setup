# Changelog

## [Unreleased]
### Fixed
- Consolidate RKE2 cleanup into one role path; keep confirmation on the playbook so extra-destructive leftover cleanup cannot run without it.
- Cleanup process kill skips the Ansible task shell; leftover path removal is unconditional; host journal files are not vacuumed.
- Cleanup path list uses the configured `paths.user.kube` instead of a hard-coded `/home/ubuntu/.kube`.

## [1.0.0] - YYYY-MM-DD
### Added
- Initial release
- Six-node cluster deployment support
- Comprehensive validation
- Automated cleanup
