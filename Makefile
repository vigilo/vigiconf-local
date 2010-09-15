NAME := vigiconf-local
CONFDIR := $(SYSCONFDIR)/vigilo/$(NAME)

all: build

include buildenv/Makefile.common

build: settings.ini build

settings.ini: settings.ini.in
	sed -e 's,@LOCALSTATEDIR@,$(LOCALSTATEDIR),;s,@SYSCONFDIR@,$(SYSCONFDIR),g' \
		$^ > $@

install: settings.ini
	$(PYTHON) setup.py install --single-version-externally-managed --root=$(DESTDIR) --record=INSTALLED_FILES
	chmod 750 $(DESTDIR)$(VARDIR)

lint: lint_pylint
#tests: tests_nose
clean: clean_python
	rm -f settings.ini


.PHONY: all clean install apidoc lint install_users install tests

