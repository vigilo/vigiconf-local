NAME := vigiconf-local
CONFDIR := $(SYSCONFDIR)/vigilo/$(NAME)
VARDIR := $(LOCALSTATEDIR)/lib/vigilo/$(NAME)

all: build

include buildenv/Makefile.common

build: settings-local.ini build

settings-local.ini: settings-local.ini.in
	sed -e 's,@LOCALSTATEDIR@,$(LOCALSTATEDIR),;s,@SYSCONFDIR@,$(SYSCONFDIR),g' \
		$^ > $@

install: settings-local.ini
	$(PYTHON) setup.py install --single-version-externally-managed --root=$(DESTDIR) --record=INSTALLED_FILES
	chmod a+rX -R $(DESTDIR)$(PREFIX)/lib*/python*/*

install_users:
	@echo "Creating the vigiconf user..."
	-groupadd vigiconf
	-useradd -s /bin/bash -M -d $(VARDIR) -g vigiconf -c 'Vigilo VigiConf user' vigiconf && dd if=/dev/random bs=1 count=12 2>/dev/null | base64 - | passwd --stdin vigiconf
	# unlock the account
	if [ `passwd -S vigiconf | cut -d" " -f2` == LK ]; then \
    	dd if=/dev/random bs=1 count=12 2>/dev/null | base64 - | passwd --stdin vigiconf ;\
	fi

install_permissions:
	chown -R vigiconf:vigiconf $(DESTDIR)$(VARDIR)

lint: lint_pylint
#tests: tests_nose
clean: clean_python
	rm -f settings-local.ini


.PHONY: all clean install apidoc lint install_users install tests

