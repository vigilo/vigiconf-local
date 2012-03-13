%define module  @SHORT_NAME@

Name:       vigilo-%{module}
Summary:    @SUMMARY@
Version:    @VERSION@
Release:    @RELEASE@%{?dist}
Source0:    %{name}-%{version}.tar.gz
URL:        @URL@
Group:      Applications/System
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-build
License:    GPLv2
Buildarch:  noarch

BuildRequires:   python-setuptools
BuildRequires:   python-babel

Requires:   python >= 2.5
Requires:   python-setuptools
Requires:   tar
Requires:   vigilo-common

Requires(pre): rpm-helper


%description
@DESCRIPTION@
This application is part of the Vigilo Project <http://vigilo-project.org>

%prep
%setup -q

%build

%install
rm -rf $RPM_BUILD_ROOT
make install_pkg \
	DESTDIR=$RPM_BUILD_ROOT \
	PREFIX=%{_prefix} \
	SYSCONFDIR=%{_sysconfdir} \
	LOCALSTATEDIR=%{_localstatedir} \
	PYTHON=%{__python}

%find_lang %{name}


%pre
%_pre_useradd vigiconf %{_localstatedir}/lib/vigilo/vigiconf /bin/bash
if [ `passwd -S vigiconf | cut -d" " -f2` == LK ]; then
    # unlock the account
    dd if=/dev/random bs=1 count=12 2>/dev/null | base64 - | passwd --stdin vigiconf >/dev/null
fi
exit 0

%post
if [ ! -d %{_localstatedir}/lib/vigilo/vigiconf/.ssh ]; then
    mkdir -p %{_localstatedir}/lib/vigilo/vigiconf/.ssh
    chown vigiconf: %{_localstatedir}/lib/vigilo/vigiconf/.ssh
    chmod 700 %{_localstatedir}/lib/vigilo/vigiconf/.ssh
    touch %{_localstatedir}/lib/vigilo/vigiconf/.ssh/authorized_keys
    chmod 600 %{_localstatedir}/lib/vigilo/vigiconf/.ssh/authorized_keys
    chown vigiconf: %{_localstatedir}/lib/vigilo/vigiconf/.ssh/authorized_keys
fi
exit 0


%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc COPYING.txt README.txt
%dir %{_sysconfdir}/vigilo
%dir %attr(-,vigiconf,vigiconf) %{_sysconfdir}/vigilo/vigiconf/
%config(noreplace) %attr(640,vigiconf,vigiconf) %{_sysconfdir}/vigilo/vigiconf/settings-local.ini
%dir %attr(-,vigiconf,vigiconf) %{_sysconfdir}/vigilo/vigiconf/new
%dir %attr(-,vigiconf,vigiconf) %{_sysconfdir}/vigilo/vigiconf/prod
%dir %attr(-,vigiconf,vigiconf) %{_sysconfdir}/vigilo/vigiconf/tmp
%dir %attr(-,vigiconf,vigiconf) %{_sysconfdir}/vigilo/vigiconf/old
%attr(755,root,root) %{_bindir}/*
%{python_sitelib}/*
%dir %{_localstatedir}/lib/vigilo
%attr(-,vigiconf,vigiconf) %{_localstatedir}/lib/vigilo/vigiconf


%changelog
* Fri Sep 17 2010 Aurelien Bompard <aurelien.bompard@c-s.fr>
- initial package
