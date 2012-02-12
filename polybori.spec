%define		vers		0.7.1
%define		patchlevel	p6
%define		name		polybori
%define		libname		%mklibname %{name} 0
%define		devname		%mklibname %{name} -d
%define		staticdevname	%mklibname %{name} -d -s
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
Version:	%{vers}.%{patchlevel}
Release:	%mkrel 4
Source0:	polybori-%{vers}.%{patchlevel}.tar.bz2
URL:		http://polybori.sourceforge.net/
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

BuildRequires:	doxygen
BuildRequires:	scons
BuildRequires:	boost-devel
BuildRequires:	ntl-devel
BuildRequires:	libm4ri-devel
BuildRequires:	texlive

%py_requires -d

Requires:	ipython >= 0.6

Patch0:		polybori-%{vers}.%{patchlevel}-sagemath.patch

%description
PolyBoRi is implemented as a C++ library for Polynomials over
Boolean Rings, which provides high-level data types for Boolean
polynomials. A python-interface yields extensible algorithms for
computing Gröbner bases over Boolean Rings.

%files
%defattr(-,root,root)
%{_bindir}/ipbori
%{_bindir}/PolyGUI
%dir %{polyboridir}
%{polyboridir}/*
%{_mandir}/man1/*

########################################################################
%package	-n python-%{name}
Group:		Development/Python
Summary:	Python bindings for PolyBoRi

%description	-n python-%{name}
PolyBoRi is a C++ library for Polynomials over Boolean Rings.
This package provides python bindings to %{name}.

%files		-n python-%{name}
%defattr(-,root,root)
%dir %{py_platlibdir}/%{name}
%{py_platlibdir}/%{name}/*

########################################################################
%package	-n %{libname}
Group:		System/Libraries
Summary:	PolyBoRi runtime libraries
Provides:	lib%{name} = %{version}-%{release}

%description	-n %{libname}
PolyBoRi runtime libraries.

%files		-n %{libname}
%defattr(-,root,root)
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
%defattr(-,root,root)
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*
%dir %{_includedir}/cudd
%{_includedir}/cudd/*
%{_libdir}/lib*.so

########################################################################
%package	-n %{staticdevname}
Group:		Development/Other
Summary:	PolyBoRi static libraries
Provides:	%{name}-static-devel = %{version}-%{release}
Requires:	lib%{name} = %{version}-%{release}
Requires:	%{name}-devel = %{version}-%{release}

%description	-n %{staticdevname}
PolyBoRi static libraries files.

%files		-n %{staticdevname}
%defattr(-,root,root)
%{_libdir}/*.a

########################################################################
%package	doc
Group:		Development/Other
Summary:	PolyBoRi documentation

%description	doc
PolyBoRi is implemented as a C++ library for Polynomials over
Boolean Rings, which provides high-level data types for Boolean
polynomials. A python-interface yields extensible algorithms for
computing Gröbner bases over Boolean Rings.

%files		doc
%defattr(-,root,root)
%dir %{_docdir}/%{name}
%{_docdir}/%{name}/*

########################################################################
%prep
%setup -q -n %{name}-%{vers}.%{patchlevel}/src/%{name}-0.7

cp ../../patches/SConstruct		./
cp ../../patches/PyPolyBoRi.py		pyroot/polybori/
cp ../../patches/COrderedIter.h		polybori/include/
cp ../../patches/nf.{h,cc}		groebner/src
cp ../../patches/plot.py		pyroot/polybori
%patch0 -p3

perl -pi -e 's|stub\.c||;' Cudd/util/Makefile
perl -pi -e 's|png12|png|;' SConstruct

%build
%scons prepare-install	CCFLAGS="%{optflags}" CPPDEFINES=UNIX=1
%scons prepare-devel	CCFLAGS="%{optflags}" CPPDEFINES=UNIX=1

%install
%scons install devel-install	CCFLAGS="%{optflags}" 	\
	PREFIX=%{buildroot}%{_prefix}			\
	PYINSTALLPREFIX=%{buildroot}%{py_platlibdir}	\
	INSTALLDIR=%{buildroot}%{polyboridir}		\
	PYPREFIX=%{py_prefix}				\
	PYTHON=%{__python}				\
	DOCDIR=%{buildroot}%{_docdir}/%{name}		\
	MANDIR=%{buildroot}%{_mandir}			\
	LIBS="-lntl"					\
	CPPDEFINES=UNIX=1				\
        CONFFILE=%{buildroot}%{_datadir}/polybori/flags.conf


chmod a+r -R %{buildroot}

# move libraries to %{_libdir}
if [ %{_prefix}/lib != %{_libdir} ]; then
    mkdir -p %{buildroot}/%{_libdir}
    mv -f %{buildroot}%{_prefix}/lib/lib* %{buildroot}/%{_libdir}
fi

perl -pi -e 's|%{buildroot}||g;' %{buildroot}%{polyboridir}/flags.conf

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

%clean
rm -rf %{buildroot}
