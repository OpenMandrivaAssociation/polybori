%define		name			polybori
%define		old_libpolybori		%mklibname polybori 0
%define		old_libpolybori_devel	%mklibname polybori -d

# NOTE: %%{_includedir}/polybori/cacheopts.h is empty on some platforms, but
# it must be present anyway.  DO NOT REMOVE IT.

Name:           polybori
Version:        0.8.3
Release:        2%{?dist}
Summary:        Framework for Boolean Rings
License:        GPLv2+
URL:            http://polybori.sourceforge.net/
Source0:        http://downloads.sourceforge.net/%{name}/%{name}-%{version}.tar.gz
# These logos were created with gimp from the official polybori logo
Source1:        %{name}-logos.tar.xz
Source2:        PolyGUI.appdata.xml
Source3:        %{name}.rpmlintrc
# This patch is specific to Fedora, although upstream helped create it.  Use
# system CUDD libraries instead of building the included CUDD sources.
Patch0:         %{name}-system-cudd.patch
# Temporary workaround for bz 974257.  Not for upstream.
Patch1:         %{name}-regex.patch

BuildRequires:	boost-devel
BuildRequires:	cudd-devel
BuildRequires:	desktop-file-utils
BuildRequires:	doxygen
BuildRequires:	libm4ri-devel
BuildRequires:	ntl-devel
BuildRequires:	png-devel
BuildRequires:	python-imaging-devel
BuildRequires:	python-qt4-devel
BuildRequires:	scons
BuildRequires:	texlive
BuildRequires:	texlive-tex4ht
BuildRequires:	python-devel
%rename %{old_libpolybori}

%global icondir %{_datadir}/icons/hicolor

%description
PolyBoRi is a special purpose computer algebra system for computations
in Boolean Rings.  The core is a C++ library, which provides high-level
data types for Boolean polynomials and related structures.  As a unique
approach, binary decision diagrams are used as internal storage type for
polynomial structures.  On top of this, we provide a Python interface
for parsing of complex polynomial systems, as well as for sophisticated
and extendable strategies for Gröbner base computation.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       boost-devel%{?_isa}
Requires:       cudd-devel%{?_isa}
%rename %{old_libpolybori_devel}

%description    devel
Development headers and libraries for %{name}.

%package        docs
Summary:        Documentation for %{name}
Requires:       %{name} = %{version}-%{release}
BuildArch:      noarch

%description    docs
Documentation for %{name}.

%package -n python-%{name}
Summary:        Python interface to %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description -n python-%{name}
Python interface to %{name}.

%package        ipbori
Summary:        Command-line interface to %{name}
Requires:       python-%{name}%{?_isa} = %{version}-%{release}
Requires:       ipython

%description    ipbori
Command-line interface to %{name}.

%package        gui
Summary:        Qt GUI for %{name}
Requires:       python-%{name}%{?_isa} = %{version}-%{release}
Requires:       PyQt4, hicolor-icon-theme

%description    gui
Qt GUI for %{name}.

%prep
%setup -q
%patch0
%patch1

# Remove private copy of system libs (Cudd and pyparsing)
rm -rf Cudd PyPolyBoRi/pyparsing.py

# Eliminate rpaths and enable NTL support
sed -e "s/'\${_relative_rpath.*/''])/" \
    -e "s/main_wrapper\.cc/& ntl_wrapper.cc/" \
    -i SConstruct

# Set up the build flags
cat > custom.py <<EOF
PREFIX = "%{_prefix}"
INSTALLDIR = "%{_datadir}/%{name}"
DOCDIR = "%{_docdir}/%{name}"
MANDIR = "%{_mandir}"
PYINSTALLPREFIX = "%{python_sitearch}"
DEVEL_PREFIX = "%{_prefix}"
DEVEL_LIB_PREFIX = "%{_libdir}"
CONFFILE = "%{_datadir}/%{name}/flags.conf"
CCFLAGS = "%{optflags} -DPBORI_USE_ORIGINAL_CUDD -DPBORI_HAVE_NTL"
CPPPATH = "-I%{_includedir}/m4ri"
SHLINKFLAGS = "$RPM_LD_FLAGS -Wl,--as-needed"
MR4I_RPM = "True"
LIBS = "-lntl -lcudd -lstdc++"
DESKTOPPATH = "%{_datadir}/applications"
PKGCONFIGPATH = "%{_libdir}/pkgconfig"
EOF

%build
scons %{?_smp_mflags} prepare-install

%install
majmin=`python -V 2>&1 | sed -r 's/.* ([[:digit:]]+\.[[:digit:]]+).*/\1/'`
major=`echo $majmin | cut -d. -f1`

sed -i "s|%{_prefix}|%{buildroot}&|" custom.py
LD_LIBRARY_PATH=$PWD/build/%{_libdir} \
  scons %{?_smp_mflags} install devel-install

# The install step doesn't set shared object permissions correctly
chmod 0755 %{buildroot}%{_libdir}/*.so.*.0.0
chmod 0755 %{buildroot}%{python_sitearch}/%{name}/dynamic/PyPolyBoRi.so

# We only want one desktop file, and it needs fixing and validating
rm -f %{buildroot}%{_datadir}/applications/PolyGUI${major}.desktop
rm -f %{buildroot}%{_datadir}/applications/PolyGUI${majmin}.desktop
sed -ri 's/Math/&;/;/(Path|MimeType)=/d' \
   %{buildroot}%{_datadir}/applications/PolyGUI.desktop
desktop-file-validate %{buildroot}%{_datadir}/applications/PolyGUI.desktop

# AppData file
mkdir -p %{buildroot}%{_datadir}/appdata
install -pm 644 %{SOURCE2} %{buildroot}%{_datadir}/appdata

# Replace the single XPM icon with multiple sizes of PNG icons
rm -fr %{buildroot}%{_datadir}/pixmaps
mkdir -p %{buildroot}%{icondir}
tar xJf %{SOURCE1} -C %{buildroot}%{icondir}

# Fixup config.h
sed -e '/PBORI_HAVE_M4RI_PNG/,$s/^#endif$/&\n#ifndef PBORI_HAVE_NTL\n#define PBORI_HAVE_NTL\n#endif/' \
    -i %{buildroot}%{_includedir}/%{name}/config.h

# Fixup flags.conf
sed -e "s|%{buildroot}||" \
    -e "/^CPPPATH/s/-I//" \
    -e "/^CPPDEFINES/s/]/, 'PBORI_USE_ORIGINAL_CUDD', 'PBORI_HAVE_NTL']/" \
    -e "/^CCFLAGS/s/'-DPBORI[_[:alpha:]]*', //g" \
    -e "/^LIBS/s/-l//g" \
    -e "/^LIBS/s/'m4ri', //" \
    -i %{buildroot}%{_datadir}/%{name}/flags.conf

# Fixup the pkgconfig files
sed -re "s,%{buildroot}|-L%{_libdir} | -lgd| gd,,g" \
    -e "s|-Ilibpolybori/include|-DPBORI_USE_ORIGINAL_CUDD|" \
    -e "s|-Igroebner/include|-DPBORI_HAVE_NTL|" \
    -e "s|build%{_libdir}[^[:blank:]]+|-lpolybori|" \
    -i %{buildroot}%{_libdir}/pkgconfig/*.pc

rm -f %{buildroot}%{_libdir}/*.a
# Workaround rpm5 and mandriva tools behavior and error about duplicate files
cp -p LICENSE README %{buildroot}%{_docdir}/%{name}/

%post gui
update-desktop-database -q >& /dev/null || :
touch --no-create %{icondir} >&/dev/null ||:
gtk-update-icon-cache %{icondir} >&/dev/null ||:

%postun gui
update-desktop-database -q >& /dev/null || :
touch --no-create %{icondir} >&/dev/null ||:
gtk-update-icon-cache %{icondir} >&/dev/null ||:

%files
%doc %{_docdir}/%{name}/LICENSE
%doc %{_docdir}/%{name}/README
%{_libdir}/lib*.so.*
%dir %{_datadir}/%{name}/
%{_datadir}/%{name}/flags.conf

%files devel
%doc ChangeLog
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/%{name}*
%{_includedir}/%{name}/
%{_includedir}/%{name}.h

%files docs
%exclude %{_docdir}/%{name}/LICENSE
%exclude %{_docdir}/%{name}/README
%{_docdir}/%{name}/

%files -n python-%{name}
%{python_sitearch}/%{name}/

%files ipbori
%{_bindir}/ipbori*
%{_mandir}/man1/ipbori*
%{_datadir}/%{name}/ipbori/

%files gui
%{_bindir}/PolyGUI*
%{_datadir}/appdata/PolyGUI.appdata.xml
%{_datadir}/applications/PolyGUI.desktop
%{_datadir}/%{name}/gui/
%{icondir}/*/apps/PolyGUI.png
%{_mandir}/man1/PolyGUI*
