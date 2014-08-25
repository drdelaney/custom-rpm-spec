# Install with rpmbuild -ba SPECS/filename.spec

# Disable stripping of binary files
%global __os_install_post %{nil}

%define __username      %(echo "$USER")
%define __email         rpmspec@loclhst.com

%define _topdir         /home/%{__username}/rpm
%define _tmppath        %{_topdir}/tmp
%define _prefix         /usr/local
%define _defaultdocdir  %{_prefix}/share/doc
%define _mandir         %{_prefix}/man

%define name      mumble-server
%define summary   Mumble is an open source voice chat software.
%define version   1.2.8
%define release   DrD
%define license   GPL
%define group     Applications/Communications
%define source0   http://downloads.sourceforge.net/project/mumble/Mumble/%{version}/murmur-static_x86-%{version}.tar.bz2
%define url       http://www.computerpr0n.com
%define vendor    Dan Delaney
%define packager  %{vendor} <%{__email}>
%define buildroot %{_tmppath}/%{name}-root
%define Murmur    murmur-static_x86-%{version}

Name:      %{name}
Version:   %{version}
Release:   %{release}
Packager:  %{packager}
Vendor:    %{vendor}
License:   %{license}
Summary:   %{summary}
Group:     %{group}
Source0:   %{source0}
URL:       %{url}
Prefix:    %{_prefix}
Buildroot: %{buildroot}
BuildArch: i386

%description
Mumble is an open source, low-latency, high quality voice chat software primarily intended for use while gaming.
Make sure to edit your /opt/mumble-server/mumble-server-default.ini!
Make sure to set/update your SuperUser password after starting the service with:
  /usr/local/sbin/murmurd -ini /opt/mumble-server/mumble-server-default.ini -supw

%prep
%setup -n %{Murmur}

%build
# Nothing to make here, move along...

%install
rm -rf %{buildroot}

# Core application
mkdir -p %{buildroot}/opt/mumble-server
mkdir -p %{buildroot}/usr/local/sbin
mkdir -p %{buildroot}/etc/rc.d/init.d/
cp -a * %{buildroot}/opt/mumble-server/
#rm -rf %{buildroot}/opt/mumble-server/murmur.x86
mv %{buildroot}/opt/mumble-server/murmur.ini %{buildroot}/opt/mumble-server/mumble-server.ini.example
ln -s /opt/mumble-server/murmur.x86 %{buildroot}/usr/local/sbin/murmurd
#%{__install} -c -m 755 murmur.x86 %{buildroot}/usr/local/sbin/murmurd

# Create dbus, rc.d, and logrotate config files
cat <<DBUSCONF > %{buildroot}/opt/mumble-server/dbus-mumble-server.conf
<!DOCTYPE busconfig PUBLIC
 "-//freedesktop//DTD D-BUS Bus Configuration 1.0//EN"
 "http://www.freedesktop.org/standards/dbus/1.0/busconfig.dtd">
<busconfig>
  <policy user="mumble-server">
    <allow own="net.sourceforge.mumble.murmur"/>
  </policy>
  <policy context="default">
    <allow send_destination="net.sourceforge.mumble.murmur"/>
    <allow receive_sender="net.sourceforge.mumble.murmur"/>
  </policy>
</busconfig>
DBUSCONF

cat <<LOGROTATECONF > %{buildroot}/opt/mumble-server/logrotate-mumble-server
/var/log/mumble-server/mumble-server-*.log {
        weekly
        rotate 7
        compress
        delaycompress
        missingok
        postrotate
		for pids in \$(ls -1 /var/run/mumble-server/*.pid); do
			kill -HUP \$(cat \${pids})
		done
        endscript
}
LOGROTATECONF

cat <<RCDCONF > %{buildroot}/etc/rc.d/init.d/mumble-server
#! /bin/sh
#
# mumble server initscript for mandriva
#
### BEGIN INIT INFO
# Provides:             mumble-server
# Required-Start:       \$network \$local_fs \$remote_fs messagebus
# Required-Stop:        \$network \$local_fs \$remote_fs messagebus
# Should-Start:         \$mysql
# Should-Stop:          \$mysql
# Default-Start:        2 3 4 5
# Default-Stop:         0 1 6
# Short-Description:    Mumble VoIP Server
# Description:          Mumble VoIP Server
### END INIT INFO

# Source function library.
. /etc/rc.d/init.d/functions

PATH=/sbin:/bin:/usr/sbin:/usr/bin
NAME=mumble-server
LOCK_FILE=/var/lock/subsys/\$NAME
PID_FILE=/var/run/\$NAME/\$NAME.pid
DAEMON=/usr/local/sbin/murmurd
USER=mumble-server

test -x \$DAEMON || exit 0

INIFILE=/opt/mumble-server/mumble-server-default.ini
DAEMON_OPTS="-ini \$INIFILE"

start() {
        printf "Starting \$NAME: "
        daemon --user \$USER \$DAEMON \$DAEMON_OPTS
        RETVAL=\$?
        echo
        [ \$RETVAL -eq 0 ] && touch \$LOCK_FILE
}

stop()  {
        printf "Shutting down \$NAME: "
        killproc \$DAEMON
        RETVAL=\$?
        echo
        if [ \$RETVAL -eq 0 ]; then
                rm -f \$LOCK_FILE
                rm -f \$PID_FILE
        fi
}


reload() {
        printf "Reloading \$NAME configuration: "
        killproc \$DAEMON -HUP
        RETVAL=\$?
        echo
}

case "\$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    status)
        status \$DAEMON
        RETVAL=\$?
        ;;
    reload)
        reload
        ;;
    restart)
        stop
        start
        ;;
    condrestart)
        if [ -f \$LOCK_FILE ]; then
            stop
            start
        fi
        ;;
    *)
        printf "Usage: %s {start|stop|restart|reload|condrestart|status}\n" "\$0"
esac

exit \$RETVAL
RCDCONF
chmod a+x %{buildroot}/etc/rc.d/init.d/mumble-server

%clean
rm -rf %{buildroot}

%post
# config files
# - main config
if [ ! -f /opt/mumble-server/mumble-server-default.ini ]; then
	cat /opt/mumble-server/mumble-server.ini.example  | sed \
		-e 's,database=,database=/opt/mumble-server/mumble-server-default.sqlite,g' \
		-e 's,#pidfile=,pidfile=/var/run/mumble-server/mumble-server-default.pid,g' \
		-e 's,#logfile=murmur.log,logfile=/var/log/mumble-server/mumble-server-default.log,g' \
		-e 's,#channelnestinglimit=10,channelnestinglimit=10,g' \
		-e 's,#uname=,uname=mumble-server,g' \
	> /opt/mumble-server/mumble-server-default.ini
fi
# - dbus
if [ -d /etc/dbus-1/system.d ]; then
	cp -u /opt/mumble-server/dbus-mumble-server.conf /etc/dbus-1/system.d/mumble-server.conf
fi
# - Log Rotate
if [ -d /etc/logrotate.d ]; then
	cp -u /opt/mumble-server/logrotate-mumble-server /etc/logrotate.d/mumble-server
fi

# add groups, dirs, perms
groupadd -g 4000 mumble-server > /dev/null 2>&1
useradd -g 4000 -G mumble-server -s /sbin/nologin -d /var/run/mumble-server -M mumble-server > /dev/null 2>&1
mkdir -p /var/log/mumble-server /var/run/mumble-server
chown -R mumble-server:mumble-server /var/log/mumble-server /opt/mumble-server /var/run/mumble-server

%files
%doc LICENSE README

%defattr(-,root,root)
/opt/mumble-server/ice/icedemo.php
/opt/mumble-server/ice/Murmur.ice
/opt/mumble-server/mumble-server.ini.example
/opt/mumble-server/dbus/murmur.pl
/opt/mumble-server/ice/weblist.php
/opt/mumble-server/dbus/weblist.pl
/opt/mumble-server/dbus-mumble-server.conf
/opt/mumble-server/logrotate-mumble-server
/opt/mumble-server/LICENSE
/opt/mumble-server/README

%defattr(755,root,root)
/opt/mumble-server/murmur.x86

%defattr(-,root,root)
/usr/local/sbin/murmurd

%defattr(755,root,root)
/etc/rc.d/init.d/mumble-server
