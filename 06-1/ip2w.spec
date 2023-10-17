License:        BSD
Vendor:         Otus
Group:          PD01
URL:            http://otus.ru/lessons/3/
Source0:        otus-%{current_datetime}.tar.gz
BuildRoot:      %{_tmppath}/otus-%{current_datetime}
Name:           ip2w
Version:        0.0.1
Release:        1
BuildArch:      noarch
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
BuildRequires: systemd
Requires: python3-pip
Requires: nginx
Summary:  IP to Weather information system


%description
...
Git version: %{git_version} (branch: %{git_branch})

%define __rpmbase   /rpmbuild
%define __etcdir    /usr/local/etc
%define __logdir    /var/log/
%define __bindir    /usr/local/ip2w/
%define __systemddir	/usr/lib/systemd/system/
%define __user      uwsgi

%prep
useradd -mU %{__user}

%install
[ "%{buildroot}" != "/" ] && rm -fr %{buildroot}
%{__mkdir} -p %{buildroot}/%{__systemddir}
pwd
%{__install} -pD -m 644 %{__rpmbase}/uwsgi.service %{buildroot}/%{__systemddir}/%{__user}.service
%{__install} -pD -m 644 -o %{__user} -g %{__user} %{__rpmbase}/%{__user}.json %{buildroot}/%{__etcdir}/%{__user}.json
%{__install} -pD -m 644 -o %{__user} -g %{__user} %{__rpmbase}/%{name}.py %{buildroot}/%{__bindir}/%{name}.py
%{__mkdir} -p %{buildroot}/%{__logdir}/%{name}
chown %{__user}:%{__user} %{buildroot}/%{__logdir}/%{name}

%post
%systemd_post %{name}.service
systemctl daemon-reload
pip install uwsgi

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun %{name}.service

%clean
[ "%{buildroot}" != "/" ] && rm -fr %{buildroot}


%files
%{__logdir}
%{__bindir}
%{__systemddir}
#%{__sysconfigdir}
%{__systemddir}/%{__user}.service
%{__etcdir}/%{__user}.json
%{__bindir}/%{name}.py
%{__logdir}/%{name}