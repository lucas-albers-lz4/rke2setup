# Changelog

## [Unreleased]
### Fixed
- Rolling RKE2 updates wait for node Ready and kube-system pods, then uncordon (no more masked kubectl failures)
- Cluster verification fails when required control-plane pods never appear
- Removed a no-op 30s wait during first control-plane token handling

## [1.0.0] - YYYY-MM-DD
### Added
- Initial release
- Six-node cluster deployment support
- Comprehensive validation
- Automated cleanup
