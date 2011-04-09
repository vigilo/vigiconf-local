%define module  @SHORT_NAME@

Name:       vigilo-%{module}
Summary:    @SUMMARY@
Version:    @VERSION@
Release:    1%{?svn}%{?dist}
Source0:    %{name}-%{version}.tar.gz
URL:        @URL@
Group:      System/Servers
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
This application is part of the Vigilo Project <http://vigilo-project.org>

%prep
%setup -q

%build
make \
    PREFIX=%{_prefix} \
    SYSCONFDIR=%{_sysconfdir} \
    LOCALSTATEDIR=%{_localstatedir} \
    PYTHON=%{__python}

%install
rm -rf $RPM_BUILD_ROOT
make install \
    DESTDIR=$RPM_BUILD_ROOT \
    PREFIX=%{_prefix} \
    SYSCONFDIR=%{_sysconfdir} \
    LOCALSTATEDIR=%{_localstatedir} \
    PYTHON=%{__python}

# Listed explicitely in %%files as %%config:
grep -v '^%{_sysconfdir}' INSTALLED_FILES \
    > INSTALLED_FILES.filtered
mv -f INSTALLED_FILES.filtered INSTALLED_FILES

%find_lang %{name}


%pre
getent group vigiconf >/dev/null || groupadd -r vigiconf
getent passwd vigiconf >/dev/null || \
    useradd -r -g vigiconf -d %{_localstatedir}/lib/vigilo/vigiconf -s /bin/bash vigiconf
# unlock the account
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
%doc COPYING
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
