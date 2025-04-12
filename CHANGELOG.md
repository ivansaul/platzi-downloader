# CHANGELOG

## v0.6.0 (2025-04-12)

### Feature

* feat: add retry decorator ([`9d698c2`](https://github.com/ivansaul/platzi-downloader/commit/9d698c20d2f4061ecc470e8e0a0a0834a1373bcd))

* feat: add overwrite option to download ([`c798e66`](https://github.com/ivansaul/platzi-downloader/commit/c798e669218311caa6670a8a2f54f0a25cbf3805))

### Fix

* fix: rename &#39;overrides&#39; to &#39;overwrite&#39; in download function ([`ad48422`](https://github.com/ivansaul/platzi-downloader/commit/ad48422a706884e25d0313b9c10fa3f98e3689ce))

* fix: streaming URLs extraction in m3u8_dl ([`e937926`](https://github.com/ivansaul/platzi-downloader/commit/e937926859c2a285627e0e863a439259f3d0e2a5))

* fix: rename &#39;overrides&#39; to &#39;overwrite&#39; in _ts_dl function ([`77bc241`](https://github.com/ivansaul/platzi-downloader/commit/77bc241e39820b8aab354c742f4ef080deccc7dc))

* fix: ffmpeg check in decorator ([`5c507c4`](https://github.com/ivansaul/platzi-downloader/commit/5c507c4da760606a1bb6e15cd060ed837c2c1cb9))

### Unknown

* Merge pull request #23 from ivansaul/develop

Add retry decorator and fix issues ([`5b5ae24`](https://github.com/ivansaul/platzi-downloader/commit/5b5ae24e497a19013004028aec41994791e36c16))

## v0.5.0 (2025-04-11)

### Documentation

* docs: add clear-cache command in usage guide ([`c29cda1`](https://github.com/ivansaul/platzi-downloader/commit/c29cda17830ea3036f5fcfc357879cb80d4cebfc))

### Feature

* feat: implement caching mechanism and CLI command to clear cache ([`a3788c4`](https://github.com/ivansaul/platzi-downloader/commit/a3788c4c18912102ba410e9d40db95a9dce8ee31))

### Refactor

* refactor: remove debug print statements from cache wrapper ([`7dbb769`](https://github.com/ivansaul/platzi-downloader/commit/7dbb769eef200c4a312557ffe9e1c640b2c4c594))

### Style

* style: format collectors for better readability ([`dcde95a`](https://github.com/ivansaul/platzi-downloader/commit/dcde95aa3c170ceb94561378c51aa20e5e7e00ce))

### Unknown

* Merge pull request #22 from ivansaul/develop

Add Cache Mechanism and Clear Command ([`5916652`](https://github.com/ivansaul/platzi-downloader/commit/59166521bd8b778f7cc4f7e343c5f9db85786b4f))

## v0.4.3 (2025-04-11)

### Chore

* chore(typing): add types-aiofiles to dev deps ([`a23edfa`](https://github.com/ivansaul/platzi-downloader/commit/a23edfaf9798481cc059a5af9a1f17e8f9df7bf0))

### Fix

* fix: update title selector for Unit data collection ([`8491c4d`](https://github.com/ivansaul/platzi-downloader/commit/8491c4dfb0e7db7782abc222d32e92b0d78971a1))

### Refactor

* refactor: replace aiohttp with rnet ([`b3e7380`](https://github.com/ivansaul/platzi-downloader/commit/b3e7380acdcf213384dffcd0e932b97a2f248805))

### Unknown

* Merge pull request #21 from ivansaul/develop

Replace aiohttp with rnet and fix Unit title selector ([`1450f92`](https://github.com/ivansaul/platzi-downloader/commit/1450f92e282e0cd7449adca601e4282771263170))

## v0.4.2 (2025-03-15)

### Chore

* chore: add .vtt files to .gitignore ([`c4cb668`](https://github.com/ivansaul/platzi-downloader/commit/c4cb668063b129dc9641910c0c4c3152abef2aea))

### Ci

* ci: update workflow to remove macOS from testing matrix ([`ab49d61`](https://github.com/ivansaul/platzi-downloader/commit/ab49d61987ab91fc54f5069831b9c76d1692dbf4))

### Documentation

* docs: add troubleshooting tips for m3u8 and ts download errors in README.md ([`0b6d170`](https://github.com/ivansaul/platzi-downloader/commit/0b6d1703ca42f5610968d3d03c95a4337c0c6c84))

### Fix

* fix: adds delays to avoid rate limiting ([`ba58014`](https://github.com/ivansaul/platzi-downloader/commit/ba58014e4c13e3301605ab1f8bb154a05f858be7))

* fix: reduce batch size for TS downloads from 10 to 5 ([`554affb`](https://github.com/ivansaul/platzi-downloader/commit/554affbb0dd189b89a67be1dc5a9caf725e69bab))

* fix: update selectors for course title and draft chapters in collectors.py ([`0100e2f`](https://github.com/ivansaul/platzi-downloader/commit/0100e2fb49304fe0ef1a2b77146897f5b36c89e2))

### Unknown

* Merge pull request #20 from ivansaul/develop

fix(ci, docs): improve collectors, downloads, and CI ([`5138848`](https://github.com/ivansaul/platzi-downloader/commit/51388483f210ad07900bef942afcff8708f5513c))

## v0.4.1 (2024-11-18)

### Fix

* fix: add handling for quiz URLs ([`6347ebb`](https://github.com/ivansaul/platzi-downloader/commit/6347ebb586269ebaaa2901cafd4d4212f77d5ff8))

### Unknown

* Merge pull request #18 from ivansaul/refactor

fix: add handling for quiz URLs ([`186fe6b`](https://github.com/ivansaul/platzi-downloader/commit/186fe6b5e860b155c1f508bae56a494fd1f1181b))

## v0.4.0 (2024-11-18)

### Chore

* chore: add slug to Unit model

Add a `slug` field to the `Unit` model and populates it using the slugified title. ([`07484ec`](https://github.com/ivansaul/platzi-downloader/commit/07484ecd20c27682b70c0a02bd2c874f42b49fa6))

* chore: add type checking with MyPy

Add MyPy and integrates it into the CI workflow. ([`d79bc90`](https://github.com/ivansaul/platzi-downloader/commit/d79bc90dd6871e1614c0cb646fdb2b6d867b76fb))

### Feature

* feat: add caching mechanism for API responses

Introduces a `Cache` class to store and retrieve API responses using persistent storage. This improves performance by avoiding redundant API calls and enables offline access to previously fetched data.  The cache uses JSON files for storage. ([`df8ef74`](https://github.com/ivansaul/platzi-downloader/commit/df8ef746f5f96879f9768cb94b79d56dc12809a3))

### Fix

* fix: TypeUnit inherit from str ([`55c71fe`](https://github.com/ivansaul/platzi-downloader/commit/55c71fee533c49b3ce04c61a0a51edceedea1d4b))

### Refactor

* refactor: replace tempfile with platformdirs for persistent session management ([`4e6e1b8`](https://github.com/ivansaul/platzi-downloader/commit/4e6e1b892755d0352072f68f450128a4fcb77348))

### Unknown

* Merge pull request #17 from ivansaul/refactor

feat: add caching mechanism for API responses ([`ec810cd`](https://github.com/ivansaul/platzi-downloader/commit/ec810cd9ef50888e1da9deb198a5471eea6e9433))

## v0.3.0 (2024-11-17)

### Documentation

* docs: removes outdated download instructions

Removes the section detailing how to download courses using a script, as this method is no longer applicable. ([`8d3e854`](https://github.com/ivansaul/platzi-downloader/commit/8d3e854a5db8a41f131177bb8d7865e81ad33dc3))

* docs: update README with updated installation and usage instructions. ([`0b9b500`](https://github.com/ivansaul/platzi-downloader/commit/0b9b500b7fa399c7ff7731e6b3ec0f6965d8523d))

### Feature

* feat: add subtitle download support

Downloads subtitles in VTT format if available alongside the video. ([`436ffd7`](https://github.com/ivansaul/platzi-downloader/commit/436ffd7f20f3eac409108875e0cea45482feceb8))

### Unknown

* Merge pull request #12 from ivansaul/refactor

feat: add subtitle download support ([`7288751`](https://github.com/ivansaul/platzi-downloader/commit/728875124fe8a45d0d5fe939bdc24fea18143f3a))

* Merge pull request #11 from ivansaul/refactor

docs: removes outdated download instructions ([`f728ab8`](https://github.com/ivansaul/platzi-downloader/commit/f728ab8117d36e11a0e922c880b202a180aefd4a))

* Merge pull request #10 from ivansaul/refactor

docs: update README with updated installation and usage instructions. ([`b74c429`](https://github.com/ivansaul/platzi-downloader/commit/b74c42966f9d88479833045c50194290f47e57ef))

## v0.2.0 (2024-11-17)

### Chore

* chore: removes unused modules and streamlines codebase ([`bcd2b06`](https://github.com/ivansaul/platzi-downloader/commit/bcd2b06d98901b9c70563f2d6c9071b794948025))

* chore: add CI workflows for testing and release ([`bc5855e`](https://github.com/ivansaul/platzi-downloader/commit/bc5855e39ecf9bf6ec5c621356432fe82053407f))

* chore: setup project configuration files

Initializes project with Poetry, sets up mypy for static type checking, and configures Ruff linter. ([`af9a825`](https://github.com/ivansaul/platzi-downloader/commit/af9a825cc234820f415775c663218d7f0e24a98a))

### Feature

* feat: add asynchronous Platzi downloader

Implements an asynchronous downloader for Platzi courses using Playwright. Includes features for login, logout, course downloading, and saving web pages as MHTML. ([`8074323`](https://github.com/ivansaul/platzi-downloader/commit/8074323d79d10eb32f6561f8459f46aafa19b0e8))

### Fix

* fix: playwright browser installation step ([`f92dcbc`](https://github.com/ivansaul/platzi-downloader/commit/f92dcbc202ab2be73563e9385e765488a08bccff))

* fix: playwright browser installation step ([`79d1e90`](https://github.com/ivansaul/platzi-downloader/commit/79d1e908bc6addaf80b8f9385dde034e532ddd4a))

* fix: playwright browser installation step ([`43360fa`](https://github.com/ivansaul/platzi-downloader/commit/43360fad1048720dca2d1f7bbcb330a9ce0e0b85))

### Unknown

* Merge pull request #9 from ivansaul/refactor

feat: add asynchronous Platzi downloader ([`7605d64`](https://github.com/ivansaul/platzi-downloader/commit/7605d64bb5151e2a4c9c5708465c4df1fd85e568))

## v0.1.0 (2024-03-06)

### Documentation

* docs(readme): update discord server link ([`2c69db4`](https://github.com/ivansaul/platzi-downloader/commit/2c69db41e0e87458faedf9a4ac899d4370a74629))

### Fix

* fix(login): implement temporary workaround for login issue ([`5f3aecd`](https://github.com/ivansaul/platzi-downloader/commit/5f3aecd30f898ce867798fa811b09bef34b89331))

* fix: remove special characters in course_name ([`6a16916`](https://github.com/ivansaul/platzi-downloader/commit/6a16916c512da4aefaab3e6c9425b4e4f7aebaf2))

* fix: expand clean_string for more special characters ([`6384d49`](https://github.com/ivansaul/platzi-downloader/commit/6384d4957870d0e2df446200a8981e49836a0169))

### Unknown

* initial commit ([`bffc0d2`](https://github.com/ivansaul/platzi-downloader/commit/bffc0d2708d5b409fabf507db7ab34c3c0fb314a))
