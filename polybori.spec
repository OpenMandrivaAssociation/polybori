%define		vers		0.6.4
%define		patchlevel	p1
%define		name		polybori
%define		libname		%mklibname %{name} 0
%define		devname		%mklibname %{name} -d
%define		staticdevname	%mklibname %{name} -d -s
%define		polyboridir	%{_datadir}/%{name}

Name:		%{name}
Group:		Sciences/Mathematics
License:	GPL
Summary:	PolyBoRi is a C++ library for Polynomials over Boolean Rings
Epoch:		1
Version:	%{vers}.%{patchlevel}
Release:	%mkrel 2
Source0:	polybori-%{vers}.%{patchlevel}.tar.bz2
URL:		http://polybori.sourceforge.net/
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

BuildRequires:	doxygen
BuildRequires:	scons
BuildRequires:	boost-devel
BuildRequires:	ntl-devel
BuildRequires:	libm4ri-devel
BuildRequires:	tex4ht
BuildRequires:	tetex-latex

%py_requires -d

Requires:	ipython >= 0.6

Patch0:		polybori-%{vers}.%{patchlevel}-sagemath.patch
Patch1:		polybori-%{vers}.%{patchlevel}-static-init-active_ring.patch

%description
PolyBoRi is implemented as a C++ library for Polynomials over
Boolean Rings, which provides high-level data types for Boolean
polynomials. A python-interface yields extensible algorithms for
computing Gröbner bases over Boolean Rings.

%files
%defattr(-,root,root)
%{_bindir}/ipbori
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
%setup -q -n %{name}-%{vers}.%{patchlevel}/src/%{name}-%{vers}

%patch0 -p3
%patch1 -p3
perl -pi -e 's|stub\.c||;' Cudd/util/Makefile

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
	CPPDEFINES=UNIX=1

chmod a+r -R %{buildroot}

# move libraries to %{_libdir}
if [ %{_prefix}/lib != %{_libdir} ]; then
    mkdir -p %{buildroot}/%{_libdir}
    mv -f %{buildroot}%{_prefix}/lib/lib* %{buildroot}/%{_libdir}
fi

perl -pi -e 's|%{buildroot}||g;' %{buildroot}%{polyboridir}/flags.conf

%clean
rm -rf %{buildroot}
