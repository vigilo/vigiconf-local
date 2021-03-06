%define module  @SHORT_NAME@

Name:       vigilo-%{module}
Summary:    @SUMMARY@
Version:    @VERSION@
Release:    @RELEASE@%{?dist}
Source0:    %{name}-%{version}@PREVERSION@.tar.gz
URL:        @URL@
Group:      Applications/System
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-build
License:    GPLv2
Buildarch:  noarch

BuildRequires:   python-distribute

Requires:   python-distribute
Requires:   tar
Requires:   vigilo-common

Requires(pre): shadow-utils


%description
@DESCRIPTION@
This application is part of the Vigilo Project <https://www.vigilo-nms.com>

%prep
%setup -q -n %{name}-%{version}@PREVERSION@

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
getent group vigiconf >/dev/null || groupadd -r vigiconf
getent passwd vigiconf >/dev/null || \
    useradd -r -g vigiconf -d %{_localstatedir}/lib/vigilo/vigiconf -s /bin/bash vigiconf
# unlock the account
if [ `passwd -S vigiconf | cut -d" " -f2` == LK ]; then
    # unlock the account
    dd if=/dev/urandom | tr -dc A-Za-z0-9 | head -c12 | passwd --stdin vigiconf >/dev/null
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
* Mon Jan 24 2011 Vincent Quéméner <vincent.quemener@c-s.fr>
- Rebuild for RHEL6.

* Fri Sep 17 2010 Aurelien Bompard <aurelien.bompard@c-s.fr>
- initial package
