%{?_javapackages_macros:%_javapackages_macros}

Summary:	Connect to AOL Instant Messenger in Java 
Name:		joscar
Version:	0.9.3r523
Release:	1
License:	BSD
Group:		Development/Java
URL:		http://joust.kano.net/
# svn checkout https://joscar.googlecode.com/svn/trunk/ joscar-read-only
# cp -far joscar-read-only joscar-0.9.3r523
# find joscar-0.9.3r523 -name \.svn -type d -exec rm -fr ./{} \; 2> /dev/null
# tar Jcf joscar-0.9.3r523.tar.xz joscar-0.9.3r523
Source0:	%{name}-%{version}.tar.xz
Source1:	%{name}-common.bnd
Source2:	%{name}-client.bnd
Source3:	%{name}-protocol.bnd
Patch0:		%{name}-bcprov-upgrade-1.54.patch
BuildArch:	noarch

BuildRequires:	jpackage-utils
BuildRequires:	ant
BuildRequires:	bouncycastle
BuildRequires:	bouncycastle-pkix
BuildRequires:	jetbrains-annotations
BuildRequires:	jsocks
BuildRequires:	junit

Requires:	java-headless
Requires:	jpackage-utils
Requires:	bouncycastle
Requires:	bouncycastle-pkix
Requires:	jsocks

%description
joscar is an easy-to-use, robust library for connecting to AOL Instant
Messenger and ICQ from Java. The library provides a simple, coherent
API to connect to the AIM/ICQ server, send and receive IM's (including
direct IM & secure IM), transfer files, and join chat rooms. The API's
event model allows for tight integration with a GUI to provide a cool
user experience.

%files
%{_javadir}/%{name}*.jar
%doc protocol/README
%doc protocol/RELNOTES
%doc protocol/USING
%doc protocol/XX_BEFORE-RELEASING_XX
%doc protocol/CHANGELOG
%doc protocol/changelog-live
%doc protocol/LICENSE

#----------------------------------------------------------------------------

%package javadoc
Summary:	Javadoc for %{name}

%description javadoc
API documentation for %{name}.

%files javadoc
%{_javadocdir}/%{name}

#----------------------------------------------------------------------------

%prep
%setup -q
# Delete all prebuild JARs and classes
find . -name "*.jar" -delete
find . -name "*.class" -delete

# Apply all patches
%patch0 -p1 -b .orig

# .bnd
sed -e "s|@VERSION@|%{version}|g" %{SOURCE1} > %{name}-common.bnd
sed -e "s|@VERSION@|%{version}|g" %{SOURCE2} > %{name}-client.bnd
sed -e "s|@VERSION@|%{version}|g" %{SOURCE3} > %{name}-protocol.bnd

# Newer version of jsocks move Proxy class into CProxy
sed -i -e 's|import socks.Proxy;|import socks.CProxy;|g' client/src/net/kano/joustsim/oscar/proxy/AimProxyInfo.java
sed -i -e 's|public Proxy|public CProxy|g' client/src/net/kano/joustsim/oscar/proxy/AimProxyInfo.java

# SocksServerSocket in jsocks uses a different api
sed -i -e 's|SocksServerSocket(proxy.createSocksProxy(),|SocksServerSocket(proxy.createSocksProxy(), (String)null,|g' \
	client/src/net/kano/joustsim/oscar/proxy/SocksServerSocketFactory.java

%build
# compile
export CLASSPATH=$(build-classpath jetbrains-annotations bcprov bcpkix jsocks junit):$CLASSPATH
%ant jars

# add OSGi manifest
for m in common client protocol
do
  java -jar $(build-classpath aqute-bnd) wrap -properties %{name}-${m}.bnd dist/%{name}-${m}.jar
  mv %{name}-${m}.bar dist/%{name}-${m}.jar
done


# add index
%jar i dist/%{name}-common.jar
%jar i dist/%{name}-client.jar
%jar i dist/%{name}-protocol.jar

# docs
%javadoc \
	-d doc -public \
	`find ./common ./protocol/src ./client/src -name '*java'`

%install
# jars
install -dm 0755 %{buildroot}%{_javadir}/
install -pm 0644 dist/%{name}-common.jar %{buildroot}%{_javadir}/%{name}-common.jar
install -pm 0644 dist/%{name}-client.jar %{buildroot}%{_javadir}/%{name}-client.jar
install -pm 0644 dist/%{name}-protocol.jar %{buildroot}%{_javadir}/%{name}-protocol.jar

# javadoc
install -dm 0755 %{buildroot}%{_javadocdir}/%{name}
cp -pr doc/* %{buildroot}%{_javadocdir}/%{name}

