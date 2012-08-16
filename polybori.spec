%define		name		polybori
%define		libname		%mklibname %{name} 0
%define		devname		%mklibname %{name} -d
%define		polyboridir	%{_datadir}/%{name}
%define		SAGE_ROOT	%{_datadir}/sage
%define		SAGE_LOCAL	%{SAGE_ROOT}/local
%define		SAGE_DEVEL	%{SAGE_ROOT}/devel
%define		SAGE_DOC	%{SAGE_DEVEL}/doc
%define		SAGE_DATA	%{SAGE_ROOT}/data
%define		SAGE_PYTHONPATH	%{SAGE_ROOT}/site-packages

Name:		%{name}
Group:		Sciences/Mathematics
License:	GPL
Summary:	PolyBoRi is a C++ library for Polynomials over Boolean Rings
Epoch:		2
Version:	0.8.2
Release:	1
URL:		http://polybori.sourceforge.net/
Source0:	http://downloads.sourceforge.net/%{name}/%{name}-%{version}.tar.gz
Source1:        %{name}.desktop
# These logos were created with gimp from the official polybori logo
Source2:        %{name}-logos.tar.xz
# This patch is specific to Fedora, although upstream helped create it.  Use
# system CUDD libraries instead of building the included CUDD sources.
Patch0:         %{name}-system-cudd.patch

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
%py_requires -d

%description
PolyBoRi is a special purpose computer algebra system for computations
in Boolean Rings.  The core is a C++ library, which provides high-level
data types for Boolean polynomials and related structures.  As a unique
approach, binary decision diagrams are used as internal storage type for
polynomial structures.  On top of this, we provide a Python interface
for parsing of complex polynomial systems, as well as for sophisticated
and extendable strategies for Gröbner base computation.

%files
%{_bindir}/ipbori
%{_bindir}/PolyGUI
%dir %{polyboridir}
%{polyboridir}/*
%{_mandir}/man1/*
%doc %{_docdir}/%{name}
%{_iconsdir}/*/apps/%{name}.png
%{_datadir}/applications/%{name}.desktop

########################################################################
%package	-n python-%{name}
Group:		Development/Python
Summary:	Python bindings for PolyBoRi

%description	-n python-%{name}
PolyBoRi is a C++ library for Polynomials over Boolean Rings.
This package provides python bindings to %{name}.

%files		-n python-%{name}
%dir %{py_platsitedir}/%{name}
%{py_platsitedir}/%{name}/*

########################################################################
%package	-n %{libname}
Group:		System/Libraries
Summary:	PolyBoRi runtime libraries
Provides:	lib%{name} = %{version}-%{release}

%description	-n %{libname}
PolyBoRi runtime libraries.

%files		-n %{libname}
%{_libdir}/lib*.so.*

########################################################################
%package	-n %{devname}
Group:		Development/Other
Summary:	PolyBoRi development files
Provides:	%{name}-devel = %{version}-%{release}
Requires:	lib%{name} = %{version}-%{release}

%description	-n %{devname}
PolyBoRi development files.

%files		-n %{devname}
%{_includedir}/polybori.h
%{_includedir}/%{name}
%{_libdir}/lib*.so

########################################################################
%prep
%setup -q

%patch0

# Remove private copy of system libs (Cudd, m4ri, and pyparsing)
rm -rf Cudd M4RI PyPolyBoRi/pyparsing.py

# Fix RPM dependency generation
for fil in gui/PolyGUI ipbori/ipbori; do
  sed "s|/usr/bin/env python|/usr/bin/python|" ${fil} > ${fil}.new
  touch -r ${fil} ${fil}.new
  mv ${fil}.new ${fil}
done

# Eliminate rpaths and enable NTL support
sed -e "s/'\${_relative_rpath.*/''])/" \
    -e "s/main_wrapper\.cc/& ntl_wrapper.cc/" \
    -i SConstruct

# Set up the build flags
cat > custom.py <<EOF
PREFIX = "%{buildroot}%{_prefix}"
INSTALLDIR = "%{buildroot}%{_datadir}/%{name}"
DOCDIR = "%{buildroot}%{_docdir}/%{name}"
MANDIR = "%{buildroot}%{_mandir}"
PYINSTALLPREFIX = "%{buildroot}%{python_sitearch}"
DEVEL_PREFIX = "%{buildroot}%{_prefix}"
DEVEL_LIB_PREFIX= "%{buildroot}%{_libdir}"
CONFFILE = "%{buildroot}%{_datadir}/%{name}/flags.conf"
CCFLAGS = "%{optflags} -DPBORI_USE_ORIGINAL_CUDD -DPBORI_HAVE_NTL"
CPPPATH = "-I%{_includedir}/m4ri"
SHLINKFLAGS = "$RPM_LD_FLAGS -Wl,--as-needed"
MR4I_RPM = "True"
LIBS = "-lntl -lcudd"
EOF

%build
%scons prepare-install

%install
%scons install devel-install

# The install step doesn't set shared object permissions correctly
chmod 0755 %{buildroot}%{_libdir}/*.so.0.0.0
chmod 0755 %{buildroot}%{python_sitearch}/%{name}/dynamic/PyPolyBoRi.so

# Install the desktop file
cp -p %{SOURCE1} .
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{name}.desktop

# Install the icons
mkdir -p %{buildroot}%{_iconsdir}
tar xJf %{SOURCE2} -C %{buildroot}%{_iconsdir}

# Move the ipbori script to bindir
rm -f %{buildroot}%{_bindir}/ipbori
sed "s|^THIS=.*|THIS=%{_datadir}/%{name}/ipbori|" \
  %{buildroot}%{_datadir}/%{name}/ipbori/ipbori > %{buildroot}%{_bindir}/ipbori
touch -r %{buildroot}%{_datadir}/%{name}/ipbori/ipbori \
  %{buildroot}%{_bindir}/ipbori
chmod a+x %{buildroot}%{_bindir}/ipbori
rm -f %{buildroot}%{_datadir}/%{name}/ipbori/ipbori

# Fixup flags.conf
sed -e "s|%{buildroot}||" \
    -e "/^CPPPATH/s/-I//" \
    -e "/^CPPDEFINES/s/]/, 'PBORI_USE_ORIGINAL_CUDD', 'PBORI_HAVE_NTL']/" \
    -e "/^CCFLAGS/s/'-DPBORI[_[:alpha:]]*', //g" \
    -e "/^LIBS/s/-l//g" \
    -e "/^LIBS/s/'m4ri', //" \
    -i %{buildroot}%{_datadir}/%{name}/flags.conf

rm -f %{buildroot}%{_bindir}/ipbori
cat > %{buildroot}%{_bindir}/ipbori << EOF
#!/bin/sh
export CUR=\`pwd\`
export DOT_SAGE="\$HOME/.sage/"
export DOT_SAGENB="\$DOT_SAGE"
mkdir -p \$DOT_SAGE/{maxima,sympow,tmp}
export SAGE_TESTDIR=\$DOT_SAGE/tmp
export SAGE_ROOT="%{SAGE_ROOT}"
export SAGE_LOCAL="%{SAGE_LOCAL}"
export SAGE_DATA="%{SAGE_DATA}"
export SAGE_DEVEL="%{SAGE_DEVEL}"
export SAGE_DOC="%{SAGE_DOC}"
export PATH=\$SAGE_LOCAL/bin:%{_datadir}/cdd/bin:\$PATH
export SINGULARPATH=%{_datadir}/singular/LIB
export SINGULAR_BIN_DIR=%{_datadir}/singular/%{_arch}
export PYTHONPATH="%{SAGE_PYTHONPATH}"
export SAGE_CBLAS=cblas
export SAGE_FORTRAN=%{_bindir}/gfortran
export SAGE_FORTRAN_LIB=\`gfortran --print-file-name=libgfortran.so\`
export SYMPOW_DIR="\$DOT_SAGE/sympow"
export LC_MESSAGES=C
export LC_NUMERIC=C
exec %{_datadir}/%{name}/ipbori/ipbori
EOF
chmod +x %{buildroot}%{_bindir}/ipbori

rm -f %{buildroot}%{_bindir}/PolyGUI
cat > %{buildroot}%{_bindir}/PolyGUI << EOF
#!/bin/sh
export CUR=\`pwd\`
export DOT_SAGE="\$HOME/.sage/"
export DOT_SAGENB="\$DOT_SAGE"
mkdir -p \$DOT_SAGE/{maxima,sympow,tmp}
export SAGE_TESTDIR=\$DOT_SAGE/tmp
export SAGE_ROOT="%{SAGE_ROOT}"
export SAGE_LOCAL="%{SAGE_LOCAL}"
export SAGE_DATA="%{SAGE_DATA}"
export SAGE_DEVEL="%{SAGE_DEVEL}"
export SAGE_DOC="%{SAGE_DOC}"
export PATH=\$SAGE_LOCAL/bin:%{_datadir}/cdd/bin:\$PATH
export SINGULARPATH=%{_datadir}/singular/LIB
export SINGULAR_BIN_DIR=%{_datadir}/singular/%{_arch}
export PYTHONPATH="%{SAGE_PYTHONPATH}"
export SAGE_CBLAS=cblas
export SAGE_FORTRAN=%{_bindir}/gfortran
export SAGE_FORTRAN_LIB=\`gfortran --print-file-name=libgfortran.so\`
export SYMPOW_DIR="\$DOT_SAGE/sympow"
export LC_MESSAGES=C
export LC_NUMERIC=C
exec %{_datadir}/%{name}/gui/PolyGUI
EOF
chmod +x %{buildroot}%{_bindir}/PolyGUI

rm -f %{buildroot}%{_libdir}/*.a
