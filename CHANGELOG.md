# [2.9.0](https://github.com/DeponesLabs/turbo-tosec/compare/v2.8.0...v2.9.0) (2026-06-01)


### Features

* **tools:** implement automated pyreverse-to-mermaid pipeline ([b2d5216](https://github.com/DeponesLabs/turbo-tosec/commit/b2d52164dcbbbb9a57c242dea980b05995b53320))

# [2.8.0](https://github.com/DeponesLabs/turbo-tosec/compare/v2.7.0...v2.8.0) (2026-05-25)


### Features

* add deprecation module for to point out deprecated code in deb progress ([2c120dc](https://github.com/DeponesLabs/turbo-tosec/commit/2c120dc4e6d24dcf47e0d0c03bf9ea9d5b4c2d48))
* add hasher module and replace crypto module ([f10e756](https://github.com/DeponesLabs/turbo-tosec/commit/f10e75604c24970fedba4b57c359b6a8fe7ec7e1))

# [2.7.0](https://github.com/DeponesLabs/turbo-tosec/compare/v2.6.5...v2.7.0) (2026-05-23)


### Features

* **core:** finalize decoupled engine architecture and stabilize direct ingestion ([56fb5ea](https://github.com/DeponesLabs/turbo-tosec/commit/56fb5ea7681031e97187e2b7f6acb265a48501de))

## [2.6.5](https://github.com/DeponesLabs/turbo-tosec/compare/v2.6.4...v2.6.5) (2026-05-23)


### Bug Fixes

* **presenter:** resolve progress bar freeze by changing condition ([9163d2f](https://github.com/DeponesLabs/turbo-tosec/commit/9163d2f5b0fcf9c72efdc4c3b9181e7142c264f0))

## [2.6.4](https://github.com/DeponesLabs/turbo-tosec/compare/v2.6.3...v2.6.4) (2026-05-23)


### Bug Fixes

* **presenter:** resolve progress bar freeze by using delta updates for tqdm ([9b80d6a](https://github.com/DeponesLabs/turbo-tosec/commit/9b80d6a7c8d089bab04b067eb629e3f2984a83be))

## [2.6.3](https://github.com/DeponesLabs/turbo-tosec/compare/v2.6.2...v2.6.3) (2026-05-23)


### Bug Fixes

* **terminal:** replace tqdm module call with class call ([80f9e4e](https://github.com/DeponesLabs/turbo-tosec/commit/80f9e4edf42c492233e8986f1c6c3ac6933b20c2))

## [2.6.2](https://github.com/DeponesLabs/turbo-tosec/compare/v2.6.1...v2.6.2) (2026-05-23)


### Bug Fixes

* **terminal:** replace tqdm module call with tqdm.twdm call & add new tests ([b9c61e4](https://github.com/DeponesLabs/turbo-tosec/commit/b9c61e4f159df79e7ef24c96bba1b6dc2788999d))

## [2.6.1](https://github.com/DeponesLabs/turbo-tosec/compare/v2.6.0...v2.6.1) (2026-05-23)


### Bug Fixes

* **config:** explicitly map turbo-tosec executable to CLI entry point to prevent UI module ImportError ([7b53237](https://github.com/DeponesLabs/turbo-tosec/commit/7b53237ad797b96a2cba9e1bf1fe26d0db540d4f))

# [2.6.0](https://github.com/DeponesLabs/turbo-tosec/compare/v2.5.1...v2.6.0) (2026-05-23)


### Bug Fixes

* get_db_version ([520f1de](https://github.com/DeponesLabs/turbo-tosec/commit/520f1deecf3faed13292664e37797ddd696a550d))


### Features

* add TosecTagEvaluator ([fbef1c1](https://github.com/DeponesLabs/turbo-tosec/commit/fbef1c16b9c5747fd0e47775f921b11224bad57c))

## [2.5.1](https://github.com/DeponesLabs/turbo-tosec/compare/v2.5.0...v2.5.1) (2026-05-19)


### Bug Fixes

* error in Callback Union Operator syntax in database.py ([cd2b7a9](https://github.com/DeponesLabs/turbo-tosec/commit/cd2b7a9d1e674532aa6fc189dd6645027f11894e))
* self.buffer type-hint ([c1894b2](https://github.com/DeponesLabs/turbo-tosec/commit/c1894b217c539828fc4b78cc7d781098256efe52))

# [2.5.0](https://github.com/DeponesLabs/turbo-tosec/compare/v2.4.0...v2.5.0) (2026-05-01)


### Features

* add Global Exception Handler ([72a108a](https://github.com/DeponesLabs/turbo-tosec/commit/72a108a85558a897fa9b8e903ae1425c5d204d85))

# [2.4.0](https://github.com/DeponesLabs/turbo-tosec/compare/v2.3.2...v2.4.0) (2026-04-30)


### Bug Fixes

* add psutil to pyproject.toml ([5ba69d4](https://github.com/DeponesLabs/turbo-tosec/commit/5ba69d4aec59a4f6e6d912f98ca68adf6365c3d5))
* adjust CI configuration and force patch version bump ([1a01b93](https://github.com/DeponesLabs/turbo-tosec/commit/1a01b932ac04636a955da4a442dbfd7bafb54172))


### Features

* add score field to TosecDat dataclass ([edc333d](https://github.com/DeponesLabs/turbo-tosec/commit/edc333d9ebb35369d5c28fc1f197e523bb20cccd))
* add slots to TosecDat dataclass ([b866d22](https://github.com/DeponesLabs/turbo-tosec/commit/b866d223fd9f29bc75cfdcf4c918caf43ff3bc39))
* add TosecDat class and domainobjects module ([03c31a0](https://github.com/DeponesLabs/turbo-tosec/commit/03c31a0e556d4adc3a93990ca37d94b57ef040cf))
* update columns fetched from tosec duckdb ([39d6a16](https://github.com/DeponesLabs/turbo-tosec/commit/39d6a167cf8d7219abf49455298add9a32ebf6fb))
* update database.DatabaseManager.resolve_game_match retval ([391d636](https://github.com/DeponesLabs/turbo-tosec/commit/391d636075e4812996c168607cf93c62cc0c181d))

## [2.3.2](https://github.com/DeponesLabs/turbo-tosec/compare/v2.3.1...v2.3.2) (2026-01-18)


### Bug Fixes

* remove unnecessary debug env packages ([d5ee5a5](https://github.com/DeponesLabs/turbo-tosec/commit/d5ee5a5955d91c12a66a47df6230dfe93917d9e6))
* remove unnecessary debug env packages ([2d02fbf](https://github.com/DeponesLabs/turbo-tosec/commit/2d02fbfd577f145fcae5997d690ddec96ebe721d))

## [2.3.1](https://github.com/DeponesLabs/turbo-tosec/compare/v2.3.0...v2.3.1) (2026-01-18)


### Bug Fixes

* trigger new release to fix linux build environment ([5840e05](https://github.com/DeponesLabs/turbo-tosec/commit/5840e05d301078cf9db77bc36ac2ba22a8c57d87))

# [2.3.0](https://github.com/DeponesLabs/turbo-tosec/compare/v2.2.1...v2.3.0) (2026-01-18)


### Bug Fixes

* **database:** fix column names in hybrid game matching strategy, fix tests ([d645f76](https://github.com/DeponesLabs/turbo-tosec/commit/d645f76cff1217526fb7dd45778851d0247a6378))


### Features

* **database:** implement hybrid game matching strategy ([056c65c](https://github.com/DeponesLabs/turbo-tosec/commit/056c65c47128c36ade33aec47de4b8735b11dfe6))

## [2.2.1](https://github.com/DeponesLabs/turbo-tosec/compare/v2.2.0...v2.2.1) (2026-01-04)


### Bug Fixes

* remove db_path parameter and add as a member var in parquet conversion funcs ([8ea3d7d](https://github.com/DeponesLabs/turbo-tosec/commit/8ea3d7d70de9b7b5e95607ae3769eed828052a6f))

# [2.2.0](https://github.com/DeponesLabs/turbo-tosec/compare/v2.1.3...v2.2.0) (2026-01-04)


### Features

* **core:** refactor session for library usage and add ingest API ([332a316](https://github.com/DeponesLabs/turbo-tosec/commit/332a316191b189dddf8e5f431cb7f7a155e42463)), closes [hi#level](https://github.com/hi/issues/level)

## [2.1.3](https://github.com/DeponesLabs/turbo-tosec/compare/v2.1.2...v2.1.3) (2025-12-28)


### Bug Fixes

* column number in pyarrow in direct mode ([33bce61](https://github.com/DeponesLabs/turbo-tosec/commit/33bce616c856a7660467753e96cf3f0163d26953))
* update test code ([f523dcb](https://github.com/DeponesLabs/turbo-tosec/commit/f523dcbe08e978a2ab09bcdb7f2cf4970c5f8ab0))

## [2.1.2](https://github.com/DeponesLabs/turbo-tosec/compare/v2.1.1...v2.1.2) (2025-12-24)


### Bug Fixes

* **console:** align turbo-tosec-ascii-logo ([f04ec19](https://github.com/DeponesLabs/turbo-tosec/commit/f04ec1907f52a980d2686323e1e85383f1cb8e2f))

## [2.1.1](https://github.com/DeponesLabs/turbo-tosec/compare/v2.1.0...v2.1.1) (2025-12-23)


### Bug Fixes

* **parser:** ensure staging output directory exists before writing ([750885c](https://github.com/DeponesLabs/turbo-tosec/commit/750885cc68b3f40bf329928e6d50a12aa005e94a))

# [2.1.0](https://github.com/DeponesLabs/turbo-tosec/compare/v2.0.0...v2.1.0) (2025-12-23)


### Bug Fixes

* **tests:** update test data and assertions for v2.0 schema compatibility ([ea16f36](https://github.com/DeponesLabs/turbo-tosec/commit/ea16f36661d41df11110106a4a4e21c38cc375db))
* **tests:** update tests to match v2.0 schema ([17e3a74](https://github.com/DeponesLabs/turbo-tosec/commit/17e3a748b6d50822b8b79a54ff043dea1a5ec1fb))


### Features

* **core:** add extended metadata columns (Category, Title, Year) ([a7baf71](https://github.com/DeponesLabs/turbo-tosec/commit/a7baf7122397485b394a641f959f423b8eb655cc))

# [2.0.0](https://github.com/DeponesLabs/turbo-tosec/compare/v1.11.2...v2.0.0) (2025-12-22)


* feat(core)!: Turbo-TOSEC v2.0 Architecture Upgrade ([ccbc1a5](https://github.com/DeponesLabs/turbo-tosec/commit/ccbc1a5acb4e557e6b7605a660b9c6b19aec8223))
* feat(core)!: Turbo-TOSEC v2.0 Architecture Upgrade ([bbe6595](https://github.com/DeponesLabs/turbo-tosec/commit/bbe6595c4019953989014a5556e0f62b35f38dae))


### BREAKING CHANGES

* This release introduces a complete architectural overhaul including Staged (ETL) and Direct (Zero-Copy) ingestion modes. CLI arguments have changed. Legacy support is retained but deprecated.
* This release introduces a complete architectural overhaul including Staged (ETL) and Direct (Zero-Copy) ingestion modes. CLI arguments have changed. Legacy support is retained but deprecated.

## [1.11.2](https://github.com/DeponesLabs/turbo-tosec/compare/v1.11.1...v1.11.2) (2025-12-22)


### Bug Fixes

* **session:** remove background monitor in DirectMode to prevent double rendering ([ee69f0b](https://github.com/DeponesLabs/turbo-tosec/commit/ee69f0ba9afd3d5ed7e6cbcd214ed51839d0b1c9))

## [1.11.1](https://github.com/DeponesLabs/turbo-tosec/compare/v1.11.0...v1.11.1) (2025-12-22)


### Bug Fixes

* correct version file path in package.json ([9e917ba](https://github.com/DeponesLabs/turbo-tosec/commit/9e917ba02494c2aa8dc1dd2edd53bf22624323f8))

# [1.11.0](https://github.com/DeponesLabs/turbo-tosec/compare/v1.10.1...v1.11.0) (2025-12-22)


### Features

* add direct mode ([2eb6cb4](https://github.com/DeponesLabs/turbo-tosec/commit/2eb6cb4a7842e00b99742f9455b9e6f13551605a))
* add retro-ascii-style-output ([0b4881c](https://github.com/DeponesLabs/turbo-tosec/commit/0b4881c0539fa0e835d73a0c1a6b3f8bd8a0d234))

## [1.10.1](https://github.com/DeponesLabs/turbo-tosec/compare/v1.10.0...v1.10.1) (2025-12-21)


### Bug Fixes

* call freeze_support in __main__ ([ecaea27](https://github.com/DeponesLabs/turbo-tosec/commit/ecaea2712f16b9923c75c4a7ec3f4ac8d777606e))

# [1.10.0](https://github.com/DeponesLabs/turbo-tosec/compare/v1.9.0...v1.10.0) (2025-12-21)


### Bug Fixes

* add freeze_support() to stop arguments required loop ([10f225f](https://github.com/DeponesLabs/turbo-tosec/commit/10f225f92550525e2f2d2ed52b429d1c5e242d13))
* requirements.txt ([e467b2e](https://github.com/DeponesLabs/turbo-tosec/commit/e467b2eb749e85767d5a3c750aca88184793a71f))


### Features

* add file size distribution analysis notebook (closes [#69](https://github.com/DeponesLabs/turbo-tosec/issues/69)) ([8735594](https://github.com/DeponesLabs/turbo-tosec/commit/87355948e16587a5fc2250432f226005088ea597))
* complete research phase with size analysis and performance benchmarks ([9e765a2](https://github.com/DeponesLabs/turbo-tosec/commit/9e765a2c95f003eac88ce3d83d658d6385df18d1))

# [1.9.0](https://github.com/DeponesLabs/turbo-tosec/compare/v1.8.3...v1.9.0) (2025-12-19)


### Bug Fixes

* database class ([070144c](https://github.com/DeponesLabs/turbo-tosec/commit/070144ce5ed25025d4aa3a0bafaa727c7d3c5f87))
* **db:** remove unsupported 'journal_mode' pragma to prevent crash ([d173967](https://github.com/DeponesLabs/turbo-tosec/commit/d17396721d4b902f7eeedb32b71650abb0812225))
* Parameter count ([d868492](https://github.com/DeponesLabs/turbo-tosec/commit/d8684927983bff55d05b81ff4cb10dce1085d4dd))
* performance regression in turbo mode ([6a352ff](https://github.com/DeponesLabs/turbo-tosec/commit/6a352ff2516553a53a5088a55a7123c9b9bda50e))
* purge remaining sqlite-specific configs incompatible with duckdb ([ad95598](https://github.com/DeponesLabs/turbo-tosec/commit/ad95598486b6b927c15eff98ead9097c5f1a3a7d))


### Features

* add cross-platform RAM detection (Windows/Linux) for turbo mode ([c4a8d81](https://github.com/DeponesLabs/turbo-tosec/commit/c4a8d8106f47bf91f45aa82b963a12eaea72bb76))
* **parser:** implement XML to temp-parquet chunking for memory optimization ([798a52f](https://github.com/DeponesLabs/turbo-tosec/commit/798a52fced3414a745c9f65db8793aab0ae797b0))
* xml chunking strategy ([fbb6b90](https://github.com/DeponesLabs/turbo-tosec/commit/fbb6b904805df1b00600420211947f789b23fb02))


### Performance Improvements

* enable high-performance duckdb pragmas (turbo mode) ([a33e47b](https://github.com/DeponesLabs/turbo-tosec/commit/a33e47bc6a140227a56d383d3da67de7ba81afac)), closes [hi#performance](https://github.com/hi/issues/performance)

## [1.8.3](https://github.com/berkacunas/turbo-tosec/compare/v1.8.2...v1.8.3) (2025-12-13)


### Bug Fixes

* handle disk-full exception ([736b9bd](https://github.com/berkacunas/turbo-tosec/commit/736b9bdfd0cfd76f0d1ad72c1a6e98b0f5cdffc7))

## [1.8.2](https://github.com/berkacunas/turbo-tosec/compare/v1.8.1...v1.8.2) (2025-12-07)


### Bug Fixes

* import version ([b26ab1d](https://github.com/berkacunas/turbo-tosec/commit/b26ab1d1228c76c9b51861e7dc77c5a5654657f0))

## [1.8.1](https://github.com/berkacunas/turbo-tosec/compare/v1.8.0...v1.8.1) (2025-12-07)


### Bug Fixes

* parse dispatcher replaced with old func call ([fe367d4](https://github.com/berkacunas/turbo-tosec/commit/fe367d4d4ce66204ae3297e4eb45d8900468ba24))

# [1.8.0](https://github.com/berkacunas/turbo-tosec/compare/v1.7.1...v1.8.0) (2025-12-06)


### Features

* add ClrMamePro (CMP) DAT files ([d6ca21d](https://github.com/berkacunas/turbo-tosec/commit/d6ca21da5305b7d8434ead2f73a75d1c39353ea9))

## [1.7.1](https://github.com/berkacunas/turbo-tosec/compare/v1.7.0...v1.7.1) (2025-12-06)


### Bug Fixes

* add parquet processing cpu limit ([fa46705](https://github.com/berkacunas/turbo-tosec/commit/fa467051fc4e8a0b3705785766f1b9580f7d2924))

# [1.7.0](https://github.com/berkacunas/turbo-tosec/compare/v1.6.0...v1.7.0) (2025-12-06)


### Features

* add parquet support ([29cb322](https://github.com/berkacunas/turbo-tosec/commit/29cb322037c273fe305d0b5c7d6497fa503acc7e))

# [1.6.0](https://github.com/berkacunas/turbo-tosec/compare/v1.5.0...v1.6.0) (2025-12-03)


### Features

* **ui:** switch progress bar from file count to byte-based tracking for accuracy ([8681edf](https://github.com/berkacunas/turbo-tosec/commit/8681edf056325ef5564dfbbe5d78628354de6385))

# [1.5.0](https://github.com/berkacunas/turbo-tosec/compare/v1.4.0...v1.5.0) (2025-12-02)


### Features

* **cli:** improve ux with auto-help on empty args and high-thread warning ([2451821](https://github.com/berkacunas/turbo-tosec/commit/245182184883e5e933209710defe9c5a07137ef2)), closes [hi#thread](https://github.com/hi/issues/thread)

# [1.4.0](https://github.com/berkacunas/turbo-tosec/compare/v1.3.6...v1.4.0) (2025-12-02)


### Features

* implement resume capability and database metadata ([c2da23e](https://github.com/berkacunas/turbo-tosec/commit/c2da23eb6c94e99c84856011ce3baaa30f8e371c))
* **importer:** implement smart resume capability with db version verification ([9e1c974](https://github.com/berkacunas/turbo-tosec/commit/9e1c97428b4aab504963eb44ec1fc1b061c10596))

## [1.3.6](https://github.com/berkacunas/turbo-tosec/compare/v1.3.5...v1.3.6) (2025-11-30)


### Bug Fixes

* **importer:** restore missing package name in import statement ([bdd7a5d](https://github.com/berkacunas/turbo-tosec/commit/bdd7a5d9ef61e7c9065369754ec9bba3a77859bc))

## [1.3.5](https://github.com/berkacunas/turbo-tosec/compare/v1.3.4...v1.3.5) (2025-11-30)


### Performance Improvements

* **importer:** add dedicated thread for progress bar timer updates ([37ed9a6](https://github.com/berkacunas/turbo-tosec/commit/37ed9a65e94bbd11e1640d612b99598e6964ba78))

## [1.3.4](https://github.com/berkacunas/turbo-tosec/compare/v1.3.3...v1.3.4) (2025-11-30)


### Bug Fixes

* add module name to imports ([43fdb72](https://github.com/berkacunas/turbo-tosec/commit/43fdb7290b6d13bdacc38943e920d07a081ae3f9))
* **ci:** install package in release workflow and fix version import path ([c7a46cc](https://github.com/berkacunas/turbo-tosec/commit/c7a46cc3e192014aea7d5004e70371cdc11cfa36))
* **cli:** print version ([ba87ae9](https://github.com/berkacunas/turbo-tosec/commit/ba87ae92d25974d454509a1a5a89192fc766c25d))
* conflict module name import ([9a5057d](https://github.com/berkacunas/turbo-tosec/commit/9a5057dcd958ba1c41c0ba2d893251098cc611ff))
* update test imports to reflect package structure ([7bb6557](https://github.com/berkacunas/turbo-tosec/commit/7bb65574a91f055d60dd2d83035b70a399594edd))

## [1.3.3](https://github.com/berkacunas/turbo-tosec/compare/v1.3.2...v1.3.3) (2025-11-30)


### Bug Fixes

* **ci:** add missing @semantic-release/exec dependency ([77e0f2a](https://github.com/berkacunas/turbo-tosec/commit/77e0f2ae5d85666b75393e725856b54c016eceb2))
* fix README.tr.md filename ([634d92e](https://github.com/berkacunas/turbo-tosec/commit/634d92e9e9ddb749760d8570317704804fa73772))

## [1.3.2](https://github.com/berkacunas/turbo-tosec/compare/v1.3.1...v1.3.2) (2025-11-29)


### Bug Fixes

* flush print ([b12b80f](https://github.com/berkacunas/turbo-tosec/commit/b12b80f85a119bc8a0c089d738fe0c0f62de19f0))

## [1.3.1](https://github.com/berkacunas/turbo-tosec/compare/v1.3.0...v1.3.1) (2025-11-29)


### Bug Fixes

* **build:** force include uuid and xml modules in hiddenimports to prevent runtime crash ([f2c71de](https://github.com/berkacunas/turbo-tosec/commit/f2c71de6afed485d0f1d61ba2627d47aa559502a))

# [1.3.0](https://github.com/berkacunas/turbo-tosec/compare/v1.2.2...v1.3.0) (2025-11-29)


### Features

* **cli:** add --about command to explain safety philosophy and usage ([b0a1c4b](https://github.com/berkacunas/turbo-tosec/commit/b0a1c4bcf3319398c7f6699b92b7494f75e293ee))

## [1.2.2](https://github.com/berkacunas/turbo-tosec/compare/v1.2.1...v1.2.2) (2025-11-29)


### Bug Fixes

* replace git token for workflow conflict ([0295e53](https://github.com/berkacunas/turbo-tosec/commit/0295e53240f40b64ccd8deac094114021fffe09c))

## [1.2.1](https://github.com/berkacunas/turbo-tosec/compare/v1.2.0...v1.2.1) (2025-11-28)


### Bug Fixes

* **build:** add duckdb to hiddenimports to prevent runtime errors ([59cf211](https://github.com/berkacunas/turbo-tosec/commit/59cf211270d28d0ae32f0d8ca626dac7a33a559e))

# [1.2.0](https://github.com/berkacunas/turbo-tosec/compare/v1.1.0...v1.2.0) (2025-11-28)


### Features

* **ci:** add automated cross-platform build workflow for single-file binaries ([cc2c60c](https://github.com/berkacunas/turbo-tosec/commit/cc2c60c80f533dc7b60ea098728ca7318dc4dc50))

# [1.1.0](https://github.com/berkacunas/turbo-tosec/compare/v1.0.0...v1.1.0) (2025-11-28)


### Features

* **importer:** add worker-based multi-threading for faster DAT parsing ([dc13c77](https://github.com/berkacunas/turbo-tosec/commit/dc13c773f44343e06339455ec285fb8674b1d20b))

# 1.0.0 (2025-11-27)


### Features

* initial project setup and core importer script ([a8aa85f](https://github.com/berkacunas/turbo-tosec/commit/a8aa85f4a9a155e0c1b0d13ba9c20018072576c9))
