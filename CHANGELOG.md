# Changelog

## [Unreleased]
### Fixed
- Consolidate RKE2 cleanup into one role path; keep confirmation on the playbook so extra-destructive leftover cleanup cannot run without it.
- Cleanup process kill skips the Ansible task shell; leftover path removal is unconditional; host journal files are not vacuumed.
<<<<<<< HEAD
- Cleanup stops kubelet before unmounting or deleting runtime paths, and removes only `paths.user.kube` (no hard-coded `/home/ubuntu/.kube`)
- Node rebuild waits for Ready=True and ready kube-system pods (Succeeded jobs ignored), then uncordons; removed leftover docs.rke2.io connectivity check
- Rolling RKE2 updates wait for node Ready and ready kube-system pods (Succeeded jobs ignored), then uncordon
- Cluster verification fails when required control-plane pods never appear
- Removed a no-op 30s wait during first control-plane token handling
=======
- Cleanup path list uses the configured `paths.user.kube` instead of a hard-coded `/home/ubuntu/.kube`.
>>>>>>> 025d20b6e303d7fa96af5ca5e4815a9765493291

## [1.0.0] - YYYY-MM-DD
### Added
- Initial release
- Six-node cluster deployment support
- Comprehensive validation
- Automated cleanup
