# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased] - DATE_PLACEHOLDER

### Added
### Removed
### Changed
### Fixed


## [0.9.11] - 2-5-2019
### Fixed
- [PR #90](https://github.com/pycom/pybytes-devices/pull/90) (pb-636): configurable watchdog


## [0.9.10] - 28-2-2019
### Fixed
- [PR #88](https://github.com/pycom/pybytes-devices/pull/88) (pb-624): ota update fix

## [0.9.9] - 25-2-2019
### Added
- [PR #84](https://github.com/pycom/pybytes-devices/pull/84) (pb-494): watchdog timer
- [PR #85](https://github.com/pycom/pybytes-devices/pull/85): LTE parameters 


## [0.9.8] - 15-2-2019
### Fixed
- [PR #79](https://github.com/pycom/pybytes-devices/pull/79) (PB-562): wifi-scan fix 


## [0.9.7] - 30-1-2019
### Changed
- updated examples: `send_virtual_pin_value` -> `send_signal`


## [0.9.6] - 23-1-2019
### Added
- LTE support
### Removed
- user and permanent flags from pybytes protocol
### Changed
- signals API: send_signal()

## [0.9.5] - 15-1-2019
### Added
- support for built-in pycom-ca.pem file
- pybytes.enable_ssl() to enable SSL with a single command

### Changed
- pybytes_protocol.py split into multiple files

### Fixed
- PB-399: wifi reconnection
- nvram_restore, catch Exceptions in __check_lora_messages


## [0.9.0] - 2018-07-19

### Added
- sigfox connection
- fix device crash on void WiFi
- Flash control over the air
- mqtt over tls support

### Changed
- pb-398-protocol-split:
  - pybytes_protocol.py size reduced
  - new file pybytes_connection.py now handles connectivity protocols
  - new file pybytes_constants.py grouping up shared constants

### Removed
- device sends only one message type info after start

## [0.8.1 - 2018-06-6]
### Changed
- Fixed mqttserver connection issue (after mqttserver is restarted)
- Fixed calc_int_version() when called with new fw 1.8.0

## [0.8.0] - 2018-05-15
### Added
- Lora extra preferences
- Version navigation.

### Changed
- Improved error handling
- Fix imports (prioritise local scripts before frozen)


[Unreleased]: https://github.com/pycom/pybytes-devices/compare/v0.9.11...HEAD
[0.9.11]: https://github.com/pycom/pybytes-devices/compare/v0.9.10...v0.9.11
[0.9.10]: https://github.com/pycom/pybytes-devices/compare/v0.9.9...v0.9.10
[0.9.9]: https://github.com/pycom/pybytes-devices/compare/v0.9.8...v0.9.9
[0.9.8]: https://github.com/pycom/pybytes-devices/compare/v0.9.7...v0.9.8
[0.9.7]: https://github.com/pycom/pybytes-devices/compare/v0.9.6...v0.9.7
[0.9.6]: https://github.com/pycom/pybytes-devices/compare/v0.9.5...v0.9.6
[0.9.5]: https://github.com/pycom/pybytes-devices/compare/v0.9.0...v0.9.5
[0.9.0]: https://github.com/pycom/pybytes-devices/compare/v0.8.1...v0.9.0
[0.8.1]: https://github.com/pycom/pybytes-devices/compare/v0.8.0...v0.8.1
[0.8.0]: https://github.com/pycom/pybytes-devices/compare/v0.3...v0.8.0

