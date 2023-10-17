#FROM quay.io/centos/centos:8
#FROM rpmbuild/centos
FROM quay.io/centos/amd64:stream8
USER root
#RUN echo "fastestmirror=true" >> /etc/dnf/dnf.conf
COPY ./repos/app.repo /etc/yum.repos.d/CentOS-Stream-AppStream.repo
COPY ./repos/base.repo /etc/yum.repos.d/CentOS-Stream-BaseOS.repo
RUN dnf install -y git rpmdevtools
#RUN useradd -m rpmbuild -u 5002 -g users -p rpmbuild
# USER rpmbuild
RUN mkdir -p /rpmbuild
COPY . /rpmbuild
#RUN chown -R rpmbuild /rpmbuild
RUN chmod -R u+x /rpmbuild
WORKDIR /rpmbuild
RUN /rpmbuild/buildrpm.sh ip2w.spec
