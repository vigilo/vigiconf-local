NAME := vigiconf-local

all: build

include buildenv/Makefile.common
VARDIR := $(LOCALSTATEDIR)/lib/vigilo/vigiconf

build: settings-local.ini build

settings-local.ini: settings-local.ini.in
	sed -e 's,@LOCALSTATEDIR@,$(LOCALSTATEDIR),;s,@SYSCONFDIR@,$(SYSCONFDIR),g' \
		$^ > $@

install: build install_python install_users install_permissions
install_pkg: build install_python_pkg

install_python: settings-local.ini $(PYTHON)
	$(PYTHON) setup.py install --record=INSTALLED_FILES
install_python_pkg: settings-local.ini $(PYTHON)
	$(PYTHON) setup.py install --single-version-externally-managed --root=$(DESTDIR)

install_users:
	@echo "Creating the vigiconf user..."
	-/usr/sbin/groupadd vigiconf
	-/usr/sbin/useradd -s /bin/bash -M -d $(VARDIR) -g vigiconf -c 'Vigilo VigiConf user' vigiconf
	# unlock the account if necessary
	if [ `passwd -S vigiconf | cut -d" " -f2` == LK ]; then \
		dd if=/dev/random bs=1 count=12 2>/dev/null | base64 - | passwd --stdin vigiconf ;\
	fi

install_permissions:
	chown -R vigiconf:vigiconf $(DESTDIR)$(VARDIR)

lint: lint_pylint
#tests: tests_nose
doc: apidoc
clean: clean_python
	rm -f settings-local.ini


.PHONY: all clean install apidoc lint install_users install install_pkg install_python install_python_pkg install_permissions tests
