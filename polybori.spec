%define		_disable_ld_as_needed	1

%define		name		polybori
%define		libname		%mklibname %{name} 0
%define		devname		%mklibname %{name} -d
%define		staticdevname	%mklibname %{name} -d -s
%define		polyboridir	%{_datadir}/%{name}

Name:		%{name}
Group:		Sciences/Mathematics
License:	GPL
Summary:	PolyBoRi is a C++ library for Polynomials over Boolean Rings
# because 0.6 was added to distro, but sagemath only works/builds with 0.5
Epoch:		1
Version:	0.5rc.p9
Release:	%mkrel 2
# browser link: http://sourceforge.net/project/downloading.php?group_id=210499&use_mirror=ufpr&filename=polybori-0.6-0rc0-2009-04-06.tar.gz&a=82369828
# Use sage version
Source0:	polybori-%{version}.tar.bz2
URL:		http://polybori.sourceforge.net/
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

BuildRequires:	doxygen
BuildRequires:	scons
BuildRequires:	boost-devel
BuildRequires:	ntl-devel
# it wants singular sources, not devel...
# BuildRequires:	singular-devel
BuildRequires:	libm4ri-devel
BuildRequires:	tex4ht

%py_requires -d

Requires:	ipython >= 0.6
Requires:	boost >= 1.33

# Edited version of patch already included in tarball
Patch0:		PyPolyBoRi.patch

# This patch is required to build when sage is already installed
# Another approach would be to set sage environment variables
Patch1:		polybori-0.5rc.p9-sagemath.patch

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
%dir %doc %{_docdir}/%{name}
%doc  %{_docdir}/%{name}/*

########################################################################
%package	-n python-%{name}
Group:		Development/Python
Summary:	Python bindings for PolyBoRi

%description	-n python-%{name}
PolyBoRi is a C++ library for Polynomials over Boolean Rings.
This package provides python bindings to %{name}.

%files		-n python-%{name}
%defattr(-,root,root)
%dir %{python_sitelib}/%{name}
%{python_sitelib}/%{name}/*

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
%setup -q -n polybori-%{version}/src/polybori-0.5rc

%patch0 -p1
%patch1 -p3

%build
%scons prepare-install
%scons prepare-devel

%install
%scons install devel-install				\
	PREFIX=%{buildroot}%{_prefix}			\
	PYINSTALLPREFIX=%{buildroot}%{py_sitedir}	\
	INSTALLDIR=%{buildroot}%{polyboridir}		\
	PYPREFIX=%{py_prefix}				\
	PYTHON=%{__python}				\
	DOCDIR=%{buildroot}%{_docdir}/%{name}		\
	MANDIR=%{buildroot}%{_mandir}			\
	LIBS="-lntl"

# stupid default attributes
chmod a+r -R %{buildroot}

# move libraries to %{_libdir}
if [ %{_prefix}/lib != %{_libdir} ]; then
    mkdir -p %{buildroot}/%{_libdir}
    mv -f %{buildroot}%{_prefix}/lib/lib* %{buildroot}/%{_libdir}
fi

%clean
rm -rf %{buildroot}

