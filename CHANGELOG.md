# Changelog

## [1.8.0](https://github.com/judoscale/judoscale-python/compare/v1.7.5...v1.8.0) (2025-01-15)


### Features

* Configure runtime container for Railway ([#98](https://github.com/judoscale/judoscale-python/issues/98)) ([6243c5b](https://github.com/judoscale/judoscale-python/commit/6243c5b0173350eba8401b28709d7b7a0d0c2318))

## [1.7.5](https://github.com/judoscale/judoscale-python/compare/v1.7.4...v1.7.5) (2024-12-05)


### Bug Fixes

* Reuse acquired connection for inspecting active workers / tasks ([#95](https://github.com/judoscale/judoscale-python/issues/95)) ([ee2588a](https://github.com/judoscale/judoscale-python/commit/ee2588a11f5470c22cb724eaf6dd80abecfa35f8))

## [1.7.4](https://github.com/judoscale/judoscale-python/compare/v1.7.3...v1.7.4) (2024-10-09)


### Bug Fixes

* Fix FastAPI auto-reloading by stacking the SIGTERM handler instead of replacing it ([e671d08](https://github.com/judoscale/judoscale-python/commit/e671d08f88890e77cbca5fb888c74e7573a77c95))

## [1.7.3](https://github.com/judoscale/judoscale-python/compare/v1.7.2...v1.7.3) (2024-07-05)


### Bug Fixes

* Bump Flask extra to &lt;4.0.0 ([#91](https://github.com/judoscale/judoscale-python/issues/91)) ([271cbad](https://github.com/judoscale/judoscale-python/commit/271cbad8ae075d13269dca6954dd7cc27868f028))
* Prevent reporter from starting in a build process ([#89](https://github.com/judoscale/judoscale-python/issues/89)) ([4c360d3](https://github.com/judoscale/judoscale-python/commit/4c360d3dfcf7714fc777cc753ab4d55b3a5de377))

## [1.7.2](https://github.com/judoscale/judoscale-python/compare/v1.7.1...v1.7.2) (2024-06-03)


### Bug Fixes

* Improve automatic queue finding for Celery ([#85](https://github.com/judoscale/judoscale-python/issues/85)) ([8662e5b](https://github.com/judoscale/judoscale-python/commit/8662e5b3e869f2568167ffebee25e030b394f9a0))

## [1.7.1](https://github.com/judoscale/judoscale-python/compare/v1.7.0...v1.7.1) (2024-05-29)


### Miscellaneous Chores

* release 1.7.1 ([1f864b8](https://github.com/judoscale/judoscale-python/commit/1f864b815ce1de9ea8fde155b1981abcb0280361))

## [1.7.0](https://github.com/judoscale/judoscale-python/compare/v1.6.2...v1.7.0) (2024-03-18)


### Features

* Expand Django version range to cover 5.x.x ([#81](https://github.com/judoscale/judoscale-python/issues/81)) ([a3e5126](https://github.com/judoscale/judoscale-python/commit/a3e5126d95b197ecd38f8ea20c4948691e0cd17e))

## [1.6.2](https://github.com/judoscale/judoscale-python/compare/v1.6.1...v1.6.2) (2023-12-01)


### Bug Fixes

* Prevent timing issues by sleeping before reporting metrics ([#78](https://github.com/judoscale/judoscale-python/issues/78)) ([56c6d2f](https://github.com/judoscale/judoscale-python/commit/56c6d2f842a6004122c950472be211564ad9e8c7))
* Report busy job metrics for correct queues ([#77](https://github.com/judoscale/judoscale-python/issues/77)) ([f13be08](https://github.com/judoscale/judoscale-python/commit/f13be080c717fe0ee9520a4303d29a3311002474))

## [1.6.1](https://github.com/judoscale/judoscale-python/compare/v1.6.0...v1.6.1) (2023-10-09)


### Bug Fixes

* Redis client configuration for RQ ([#75](https://github.com/judoscale/judoscale-python/issues/75)) ([e961b4d](https://github.com/judoscale/judoscale-python/commit/e961b4daf1eaf0a924ea52e06ec6c4ee07f0aa59))

## [1.6.0](https://github.com/judoscale/judoscale-python/compare/v1.5.1...v1.6.0) (2023-10-02)


### Features

* Allow setting Judoscale log level using an env var ([#72](https://github.com/judoscale/judoscale-python/issues/72)) ([b9e9046](https://github.com/judoscale/judoscale-python/commit/b9e9046f0c64ec7cf6d0e0d7367ab2d263f118d6))


### Bug Fixes

* judoscale.rq not getting registered in Django &lt; 3.2 ([#74](https://github.com/judoscale/judoscale-python/issues/74)) ([59fb8e1](https://github.com/judoscale/judoscale-python/commit/59fb8e1aa5906e09da5710a5e81dca58a38971b5))

## [1.5.1](https://github.com/judoscale/judoscale-python/compare/v1.5.0...v1.5.1) (2023-08-26)


### Bug Fixes

* Gracefully handle missing task ID ([#70](https://github.com/judoscale/judoscale-python/issues/70)) ([8292add](https://github.com/judoscale/judoscale-python/commit/8292add5c7a91b766ed107c38bbffd291425ea5f))

## [1.5.0](https://github.com/judoscale/judoscale-python/compare/v1.4.2...v1.5.0) (2023-07-18)


### Features

* Add support for containers running on AWS ECS ([#65](https://github.com/judoscale/judoscale-python/issues/65)) ([3a6a356](https://github.com/judoscale/judoscale-python/commit/3a6a356597da6bcb25cbb5adf0116ea38f726a0f))

## [1.4.2](https://github.com/judoscale/judoscale-python/compare/v1.4.1...v1.4.2) (2023-06-26)


### Bug Fixes

* Prevent reporter from running if Config.is_enabled is False ([#63](https://github.com/judoscale/judoscale-python/issues/63)) ([daebe4b](https://github.com/judoscale/judoscale-python/commit/daebe4bbbbe0282d8d8bc5b4aef49a3744a81b71))

## [1.4.1](https://github.com/judoscale/judoscale-python/compare/v1.4.0...v1.4.1) (2023-04-28)


### Bug Fixes

* Handle missing API_BASE_URL ([#60](https://github.com/judoscale/judoscale-python/issues/60)) ([79f2753](https://github.com/judoscale/judoscale-python/commit/79f2753f6d25ffbc73da158c5ebddf8c8d561d60))

## [1.4.0](https://github.com/judoscale/judoscale-python/compare/v1.3.0...v1.4.0) (2023-04-19)


### Features

* Generic asgi request queue time middleware ([#57](https://github.com/judoscale/judoscale-python/issues/57)) ([5660ca6](https://github.com/judoscale/judoscale-python/commit/5660ca6a1fd7f65b317a48195380220a07cd4686))

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
