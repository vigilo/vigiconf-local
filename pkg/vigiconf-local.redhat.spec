%define module  vigiconf-local
%define name    vigilo-%{module}
%define version 2.0.0
%define release 1%{?svn}%{?dist}

%define pyver 26
%define pybasever 2.6
%define __python /usr/bin/python%{pybasever}
%define __os_install_post %{__python26_os_install_post}
%{!?python26_sitelib: %define python26_sitelib %(python26 -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:       %{name}
Summary:    Local client for VigiConf
Version:    %{version}
Release:    %{release}
Source0:    %{module}.tar.bz2
URL:        http://www.projet-vigilo.org
Group:      System/Servers
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-build
License:    GPLv2
Buildarch:  noarch

Requires:   python26-distribute
Requires:   tar
Requires:   vigilo-common

Requires(pre): shadow-utils


%description
This program installs the configuration pushed by VigiConf.
applications used in the supervision system.
This application is part of the Vigilo Project <http://vigilo-project.org>

%prep
%setup -q -n %{module}

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


%pre
getent group vigiconf >/dev/null || groupadd -r vigiconf
getent passwd vigiconf >/dev/null || \
    useradd -r -g vigiconf -d %{_localstatedir}/lib/vigilo/vigiconf -s /bin/bash vigiconf
# unlock the account
if [ `passwd -S vigiconf | cut -d" " -f2` == LK ]; then
    dd if=/dev/random bs=1 count=12 2>/dev/null | base64 - | passwd --stdin vigiconf >/dev/null
fi
exit 0


%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc COPYING
%dir %{_sysconfdir}/vigilo
%dir %attr(-,vigiconf,vigiconf) %{_sysconfdir}/vigilo/vigiconf/
%config(noreplace) %attr(640,vigiconf,vigiconf) %{_sysconfdir}/vigilo/vigiconf/settings-local.ini
%dir %attr(-,vigiconf,vigiconf) %{_sysconfdir}/vigilo/vigiconf/new
%dir %attr(-,vigiconf,vigiconf) %{_sysconfdir}/vigilo/vigiconf/prod
%dir %attr(-,vigiconf,vigiconf) %{_sysconfdir}/vigilo/vigiconf/tmp
%{_bindir}/*
%{python26_sitelib}/*
%dir %{_localstatedir}/lib/vigilo
%attr(-,vigiconf,vigiconf) %{_localstatedir}/lib/vigilo/vigiconf


%changelog
* Fri Sep 17 2010 Aurelien Bompard <aurelien.bompard@c-s.fr>
- initial package
