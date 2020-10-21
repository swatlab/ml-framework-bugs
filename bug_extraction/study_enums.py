from collections import namedtuple
import dataclasses

@dataclasses.dataclass(order=True)
class StudyPhase1Field:
    '''Class representing bug information for phase 1'''
    framework: str = None
    # (manual) Give a name representing the issue
    bug_name: str = None
    issue_number: int = None
    pr_number: int = None
    buggy_commit: str = None
    # Commit (revision) at which bug contains all the fixes
    corrected_commit: str = None


@dataclasses.dataclass(order=True)
class StudyPhase2Field:
    '''Class representing bug information for phase 2.'''
    link: str = None
    release: str = None
    # Name of the pull request
    pr_name: str = None
    # Information about the fix provided in the release information (usually how the authors explain the bug fix in release notes)
    release_note_description: str = None


@dataclasses.dataclass(order=True)
class StudyPhase3Field:
    description: str = None
    comment: str = None

