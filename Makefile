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

install_users:
	@echo "Creating the $(NAME) user..."
	-groupadd $(NAME)
	-useradd -s /bin/bash -M -d $(VARDIR) -g $(NAME) -c 'Vigilo VigiConf user' $(NAME)

install_permissions:
	chown -R $(NAME):$(NAME) $(DESTDIR)$(VARDIR)

lint: lint_pylint
#tests: tests_nose
clean: clean_python
	rm -f settings-local.ini


.PHONY: all clean install apidoc lint install_users install tests

