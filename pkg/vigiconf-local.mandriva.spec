%define module  vigiconf-local
%define name    vigilo-%{module}
%define version 2.0.0
%define release 1%{?svn}%{?dist}

Name:       %{name}
Summary:    Local client for VigiConf
Version:    %{version}
Release:    %{release}
Source0:    %{name}-%{version}.tar.gz
URL:        http://www.projet-vigilo.org
Group:      System/Servers
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-build
License:    GPLv2

Requires(pre): rpm-helper

Requires:   python >= 2.5
Requires:   python-setuptools
Requires:   tar
Requires:   vigilo-common
Buildarch:  noarch


%description
This program installs the configuration pushed by VigiConf.
This application is part of the Vigilo Project <http://vigilo-project.org>

%prep
%setup -q

%build
make \
	PREFIX=%{_prefix} \
	SYSCONFDIR=%{_sysconfdir} \
	LOCALSTATEDIR=%{_localstatedir} \
	PYTHON=%{_bindir}/python

%install
rm -rf $RPM_BUILD_ROOT
make install \
	DESTDIR=$RPM_BUILD_ROOT \
	PREFIX=%{_prefix} \
	SYSCONFDIR=%{_sysconfdir} \
	LOCALSTATEDIR=%{_localstatedir} \
	PYTHON=%{_bindir}/python

# Listed explicitely in %%files as %%config:
grep -v '^%{_sysconfdir}' INSTALLED_FILES \
	> INSTALLED_FILES.filtered
mv -f INSTALLED_FILES.filtered INSTALLED_FILES


%pre
%_pre_useradd vigiconf %{_localstatedir}/lib/vigilo/vigiconf /bin/bash
if [ `passwd -S vigiconf | cut -d" " -f2` == LK ]; then
    # unlock the account
    dd if=/dev/random bs=1 count=12 2>/dev/null | base64 - | passwd --stdin vigiconf >/dev/null
fi
exit 0


%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc COPYING
%dir %{_sysconfdir}/vigilo
%dir %attr(-,vigiconf,vigiconf) %{_sysconfdir}/vigilo/vigiconf/
%config(noreplace) %attr(640,vigiconf,vigiconf) %{_sysconfdir}/vigilo/vigiconf/settings-local.ini
%dir %attr(-,vigiconf,vigiconf) %{_sysconfdir}/vigilo/vigiconf/new
%dir %attr(-,vigiconf,vigiconf) %{_sysconfdir}/vigilo/vigiconf/prod
%dir %attr(-,vigiconf,vigiconf) %{_sysconfdir}/vigilo/vigiconf/tmp
%dir %attr(-,vigiconf,vigiconf) %{_sysconfdir}/vigilo/vigiconf/old
%{_bindir}/*
%{python_sitelib}/*
%dir %{_localstatedir}/lib/vigilo
%attr(-,vigiconf,vigiconf) %{_localstatedir}/lib/vigilo/vigiconf


%changelog
* Fri Sep 17 2010 Aurelien Bompard <aurelien.bompard@c-s.fr>
- initial package
