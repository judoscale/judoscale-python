# Changelog

## [1.3.0](https://github.com/judoscale/judoscale-python/compare/v1.2.2...v1.3.0) (2023-04-10)


### Features

* Add FastAPI support as ASGI middleware ([#54](https://github.com/judoscale/judoscale-python/issues/54)) ([1b306a1](https://github.com/judoscale/judoscale-python/commit/1b306a1c357eea876bff30cd02b9bdd5a97b453f))
* Add support for tracking busy jobs ([#48](https://github.com/judoscale/judoscale-python/issues/48)) ([ad7b3ad](https://github.com/judoscale/judoscale-python/commit/ad7b3adf4c9c3e8b90735fa3498e25c3f6c6b0b6))

## [1.2.2](https://github.com/judoscale/judoscale-python/compare/v1.2.1...v1.2.2) (2023-04-03)


### Bug Fixes

* Fix accessing missing Celery task properties ([#52](https://github.com/judoscale/judoscale-python/issues/52)) ([1efd53e](https://github.com/judoscale/judoscale-python/commit/1efd53e0c345dd2e79760f6ac2ff22973a99b614))

## [1.2.1](https://github.com/judoscale/judoscale-python/compare/v1.2.0...v1.2.1) (2023-03-28)


### Bug Fixes

* Fix pulling incorrect configuration values for Celery ([2b6cbc1](https://github.com/judoscale/judoscale-python/commit/2b6cbc199e7744f801033b6536cc4375d58c8562))

## [1.2.0](https://github.com/judoscale/judoscale-python/compare/v1.1.0...v1.2.0) (2023-03-27)


### Features

* Handle ambiguous timestamp values in X-Request-Start ([ed56895](https://github.com/judoscale/judoscale-python/commit/ed56895c95269fafbb54c914d588787081458937))
* Job backend configuration options ([e2d3262](https://github.com/judoscale/judoscale-python/commit/e2d3262fa0b61acc69235a31cff42ec630514509))
* Render integration ([cd62c24](https://github.com/judoscale/judoscale-python/commit/cd62c24c06a0edce942162a1edd8e6229a5c2216))


### Bug Fixes

* Handle minimum Redis version ([a35a38a](https://github.com/judoscale/judoscale-python/commit/a35a38ac4a95615beaf6ac88a0a429b644b86051))

## [1.1.0](https://github.com/judoscale/judoscale-python/compare/v1.0.0...v1.1.0) (2023-03-08)


### Features

* Add RQ support ([d30ba24](https://github.com/judoscale/judoscale-python/commit/d30ba247de26c6f60a2755087513a1890c2cd1a5))


### Documentation

* Improve README ([b493359](https://github.com/judoscale/judoscale-python/commit/b4933597e8cc45ede5d1664a323a477229af9922))

## [1.0.0](https://github.com/judoscale/judoscale-python/compare/v0.1.1...v1.0.0) (2023-02-20)


### Features

* Add Celery support ([09502ab](https://github.com/judoscale/judoscale-python/commit/09502abdfd27b20ee289e52947a2478e10d2fd8d))
* Include adapter metadata in report payload ([2e8cf9a](https://github.com/judoscale/judoscale-python/commit/2e8cf9a50638d4115c1038e9db0688b3a8332034))
* Installable as extras ([6078e79](https://github.com/judoscale/judoscale-python/commit/6078e799a4e4dccfea487ba4055fecef2cebadef))
* Introduce collector abstraction ([eb88b9f](https://github.com/judoscale/judoscale-python/commit/eb88b9f95a25993a44c784f93da2200c30f4d5c1))

## [0.1.1](https://github.com/judoscale/judoscale-python/compare/v0.1.0...v0.1.1) (2023-01-09)


### Miscellaneous Chores

* Update release action to publish to PyPI ([c278b10](https://github.com/judoscale/judoscale-python/commit/c278b10defe661d09bd67adf0fd0359afd602ba9))

## 0.1.0 (2023-01-05)


### Features

* Introduce Judoscale support for Flask as a Flask extension ([d5091eb](https://github.com/judoscale/judoscale-python/commit/d5091eb4865c024110af7584d233c32c511f7349))


### Bug Fixes

* Update API path for posting metrics ([#24](https://github.com/judoscale/judoscale-python/issues/24)) ([fe5e90d](https://github.com/judoscale/judoscale-python/commit/fe5e90d679b9658652863e1e852a264b3d467741))
