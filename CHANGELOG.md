# Changelog for Syllabee

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2024-03-18

### Added

#### General
- Region loader engine. All page content (regardless of page) is now loaded dynamically based on three regions: content, profile, and toc (Table of Contents).
- Removed sidebar and replaced it with narrow navbar that's always available (regardless of page or window view size).

#### Editor
- Due to stronger region definition
- Multiple view options for Master Syllabi: interactive and traditional. Syllabee now supports an interactive syllabus!
- Added Quill editor to previous HTML supported inputs, providing a more consistent and user-friendly way of entering content.
- Added support for canned Messages that can be opened in a local email client for sending to students (or anyone else).
- Added ability to view every toast notification since last page load. 
- Added support for viewing a student's progress and attempts for an interactive syllabus.

### Changed

#### General
- A LOT! Base apps completely redesigned with an Editor/Viewer split. Editor interface is strictly for instructors and admins. Viewer interface serves syllabi and offers ability to print.

#### Editor
- Integrated editor interface with previous syllabus interface for a fully unified user interface (UUI).
- Changed Master Syllabus publishing process to a locking process. Students can view syllabi regardless of lock status. However, locking conducts a series of checks to verify the validity of the master syllabus. 
- All hard-coded error checks (and indicators) were removed from the UUI (due to locking mechanism checks).
- Master Bonds now have a visibility option which determines availability for students. 
- Removed CourseSyllabusBlocks, FileBlocks, and ListBlocks.

### Fixed

- Fixed issues #1, #7, #10, #11, #15, and #16.

## [0.3.0] - 2023-06-12

### Added

- When loading a printable syllabus, a new splash screen displays providing an option for viewing an Abridged Syllabus or the Full one.

### Changed

- Options for selecting an Abridged or Full Syllabus were removed from various drop-downs (due to the new splash screen allowing the user to pick for themselves).

### Fixed

- Fixed issue where multiple schedules were being displayed for the same section on the Schedules tab (Issue #13).
- Fixed several issues with the Lookup tool where various drop-down menus were not being populated correctly (Issue #14).
- Fixed an issue with filtering sections by terms that had been archived. 

## [0.2.0] - 2023-01-17

### Added

- Added a description field to FileBlocks.
- Added segment names to the table of contents section on a static syllabus.
- Added copyright and version information to the login page and to a static syllabus page (Issue #5).
- Added option to associate a static syllabus file with a section for archival purposes.
- Added new module for looking up syllabi by instructor, term (as well as course and section), or by searching directly.
- Added support for unauthenticated users to change the theme on a syllabus.
- Added support for an abridged syllabus.

### Changed

- Changed the header and footer colors of modals and offcanvases.
- Changed modals and offcanvases to feature more defined borders and added a shadow to both.
- Changed the section filter modal so all terms are displayed (including archived terms).

### Fixed

- Fixed issue where icon was not correctly showing for GradeDeterminationBlock.
- Fixed issue with the block content library which prevented adding dynamic blocks to segments that support them.
- Fixed issue with the schedule which prevented proper sanitization of all rows (specifically for the due date column).
- Fixed an issue where a midpoint break on a schedule (within a ScheduleBlock) would cause a unit to not span correctly (Issue #8).
- Fixed issue where several filter form classes had database lookups that weren't in a function which caused an error when making migrations.
- Fixed issue with the add menu not displaying properly on a segment with no associated blocks (Issue #4).
- Fixed issue where office hours were not correctly displayed on syllabi that were not full length (Issue #2).
- Corrected terminology within messages when a Master Syllabus has no segments associated with it or other others.
- Corrected the coloring of links on a static syllabus card.
- Prevented assignments without points associated with them from being included in GradeDeterminationBlocks.

## [0.1.0] - 2022-12-09

### Added

- Initial release with only static syllabus support.

[unreleased]: https://github.com/lsmith2-edison/syllabee/compare/v1.1.0...HEAD
[0.1.0]: https://github.com/lsmith2-edison/syllabee/releases/tag/v0.1.0