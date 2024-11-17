# CHANGELOG

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
