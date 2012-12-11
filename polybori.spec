%define		name			polybori
%define		libpolybori		%mklibname %{name} 0
%define		libpolybori_devel	%mklibname %{name} -d
%define		polyboridir		%{_datadir}/%{name}
%define		SAGE_ROOT		%{_datadir}/sage
%define		SAGE_LOCAL		%{SAGE_ROOT}/local
%define		SAGE_DEVEL		%{SAGE_ROOT}/devel
%define		SAGE_DOC		%{SAGE_DEVEL}/doc
%define		SAGE_DATA		%{SAGE_ROOT}/data
%define		SAGE_PYTHONPATH		%{SAGE_ROOT}/site-packages

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
%package	-n %{libpolybori}
Group:		System/Libraries
Summary:	PolyBoRi runtime libraries
Provides:	lib%{name} = %{version}-%{release}

%description	-n %{libpolybori}
PolyBoRi runtime libraries.

%files		-n %{libpolybori}
%{_libdir}/lib*.so.*

########################################################################
%package	-n %{libpolybori_devel}
Group:		Development/Other
Summary:	PolyBoRi development files
Provides:	%{name}-devel = %{version}-%{release}
Requires:	lib%{name} = %{version}-%{release}

%description	-n %{libpolybori_devel}
PolyBoRi development files.

%files		-n %{libpolybori_devel}
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


%changelog
* Fri Aug 17 2012 Paulo Andrade <pcpa@mandriva.com.br> 2:0.8.2-1
+ Revision: 815180
- Update to packaging matching http://pkgs.fedoraproject.org/cgit/polybori.git

* Sun Feb 12 2012 Paulo Andrade <pcpa@mandriva.com.br> 2:0.7.1.p6-4
+ Revision: 773605
- Rebuild with boost 1.48 due to missing boost 1.46 libraries in mirrors.

* Sat Nov 05 2011 Paulo Andrade <pcpa@mandriva.com.br> 2:0.7.1.p6-3
+ Revision: 720479
- Remove upstream patch/hack to force to link with -lpng12.

* Sat Nov 05 2011 Paulo Andrade <pcpa@mandriva.com.br> 2:0.7.1.p6-2
+ Revision: 720397
- Install flags.conf file.

* Sat Nov 05 2011 Paulo Andrade <pcpa@mandriva.com.br> 2:0.7.1.p6-1
+ Revision: 718211
- Update to latest upstream release.

* Wed Aug 03 2011 Paulo Andrade <pcpa@mandriva.com.br> 2:0.7.0.p3-3
+ Revision: 692938
- Correct ipbori script to set search path to sage binaries first

* Wed Jun 01 2011 Paulo Andrade <pcpa@mandriva.com.br> 2:0.7.0.p3-2
+ Revision: 682294
- Correct scripts that sets sagemath environment variables

* Tue May 31 2011 Paulo Andrade <pcpa@mandriva.com.br> 2:0.7.0.p3-1
+ Revision: 682024
- Update to latest upstream release.

* Thu Mar 17 2011 Funda Wang <fwang@mandriva.org> 2:0.6.4.p6-2
+ Revision: 645716
- rebuild for new boost

* Mon Mar 07 2011 Paulo Andrade <pcpa@mandriva.com.br> 2:0.6.4.p6-1
+ Revision: 642753
- Update to newer patchlevel

* Tue Mar 01 2011 Paulo Andrade <pcpa@mandriva.com.br> 2:0.6.4.p4-3
+ Revision: 641193
- Rebuild with texlive

* Wed Nov 03 2010 Paulo Andrade <pcpa@mandriva.com.br> 2:0.6.4.p4-2mdv2011.0
+ Revision: 592997
+ rebuild (emptylog)

* Thu Sep 23 2010 Paulo Andrade <pcpa@mandriva.com.br> 2:0.6.4.p4-1mdv2011.0
+ Revision: 580794
- Rework and adapt sagemath patches to correct crashes in doctests

* Wed Sep 22 2010 Paulo Andrade <pcpa@mandriva.com.br> 1:0.6.4.p4-1mdv2011.0
+ Revision: 580443
- Update to patchlevel 4

* Wed Aug 25 2010 Funda Wang <fwang@mandriva.org> 1:0.6.4.p1-4mdv2011.0
+ Revision: 573033
- rebuild

* Thu Aug 05 2010 Funda Wang <fwang@mandriva.org> 1:0.6.4.p1-3mdv2011.0
+ Revision: 566294
- rebuild for new boost

* Wed Jul 14 2010 Paulo Andrade <pcpa@mandriva.com.br> 1:0.6.4.p1-2mdv2011.0
+ Revision: 553402
+ rebuild (emptylog)

* Wed Jul 14 2010 Paulo Andrade <pcpa@mandriva.com.br> 1:0.6.4.p1-1mdv2011.0
+ Revision: 552982
- Update to version 0.6.4, patchlevel 1.

* Mon Feb 08 2010 Anssi Hannula <anssi@mandriva.org> 1:0.6.3.20091028-7mdv2010.1
+ Revision: 501882
- rebuild for new boost
- remove unneeded explicit dependency on boost; autodependencies work
  correctly

* Thu Feb 04 2010 Paulo Andrade <pcpa@mandriva.com.br> 1:0.6.3.20091028-6mdv2010.1
+ Revision: 500942
- Rediff sagemath patch

* Wed Feb 03 2010 Funda Wang <fwang@mandriva.org> 1:0.6.3.20091028-5mdv2010.1
+ Revision: 500340
- rebuild for new boost

* Mon Feb 01 2010 Paulo Andrade <pcpa@mandriva.com.br> 1:0.6.3.20091028-4mdv2010.1
+ Revision: 499392
- Statically initialize global BooleEnv::ring_type active_ring

* Sat Jan 30 2010 Paulo Andrade <pcpa@mandriva.com.br> 1:0.6.3.20091028-3mdv2010.1
+ Revision: 498369
- Rebuild forcing use of Mandriva default optflags

* Wed Jan 27 2010 Paulo Andrade <pcpa@mandriva.com.br> 1:0.6.3.20091028-2mdv2010.1
+ Revision: 497395
- Rebuild and remove no longer needed _disable_ld_as_needed

* Fri Jan 22 2010 Paulo Andrade <pcpa@mandriva.com.br> 1:0.6.3.20091028-1mdv2010.1
+ Revision: 495108
- Update to polybori 0.6.3 from 20091028

* Tue Nov 17 2009 Paulo Andrade <pcpa@mandriva.com.br> 1:0.6.3.20090827-1mdv2010.1
+ Revision: 466704
- Update to polybori 0.6.3 from 20090827
- Merge sage patches into a single one
- Install python files in arch specific directory as there is a shared object
- Correct problem with documentation being installed twice
- Correct /usr/share/polybori/flags.conf (that is now used by sage 4.2 build)
- Correct ipbori to setup sage environment

* Wed Sep 09 2009 Paulo Andrade <pcpa@mandriva.com.br> 1:0.5rc.p9-6mdv2010.0
+ Revision: 435927
+ rebuild (emptylog)

* Sat Sep 05 2009 Paulo Andrade <pcpa@mandriva.com.br> 1:0.5rc.p9-4mdv2010.0
+ Revision: 431901
+ rebuild (emptylog)

* Fri Sep 04 2009 Paulo Andrade <pcpa@mandriva.com.br> 1:0.5rc.p9-2mdv2010.0
+ Revision: 431728
- allow rebuild when sagemath is installed
- link libraries with ntl

* Fri Sep 04 2009 Paulo Andrade <pcpa@mandriva.com.br> 1:0.5rc.p9-1mdv2010.0
+ Revision: 429130
- update to patchlevel 9

  + Funda Wang <fwang@mandriva.org>
    - rebuild for new libboost

* Wed Jul 15 2009 Paulo Andrade <pcpa@mandriva.com.br> 1:0.5-3mdv2010.0
+ Revision: 396471
- Update to latest upstream patchlevel 8.

* Tue May 19 2009 Paulo Andrade <pcpa@mandriva.com.br> 1:0.5-2mdv2010.0
+ Revision: 377421
+ rebuild (emptylog)

* Thu May 14 2009 Paulo Andrade <pcpa@mandriva.com.br> 1:0.5-1mdv2010.0
+ Revision: 375857
- Use an older version of polybori that works with sagemath.

* Thu May 14 2009 Paulo Andrade <pcpa@mandriva.com.br> 0.6-2mdv2010.0
+ Revision: 375808
- Initial import of polybori version 0.6.
  PolyBoRi is a C++ library for Polynomials over Boolean Rings
  http://polybori.sourceforge.net/
- polybori

