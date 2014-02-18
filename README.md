custom-rpm-sec
==============

My custom RPM SPEC files for CentOS/RHEL 5/6

Use these at your own will. They are provided as-is.
I will not be held accountable if these alter your systems in a way you do not like.

To create your rpmbuild file structure, use:
mkdir ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS,tmp}

Make sure the .spec files are stored in the SPECS folder.
You will need to manually download any source files to the SOURCES diretory.
Following the URL in the .spec file should yeild the sources you need.

To build sources, make sure you have the following rpms installed:
rpm-build, make, gcc (as well as other development tools)

To create the rpm, simply cd into ~/rpmbuild, and run rpmbuild -ba SPECS/filename.spec.

If any of these have helped you, please feel free to donate!

BTC: 1HYN6gK4hmykT9Y7SBVMyheNKPzuq5fi3v

LTC: LQ7dnDk327ENnduTAVioiM9RpGQS5fAKg3

DOGE: DJihu6BcKG1XZVk4JY3c8ZeRtC6wLLbXab
