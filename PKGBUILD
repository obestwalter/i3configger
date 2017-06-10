# $Id$
# Maintainer: Oliver Bestwalter <oliver@bestwalter.de>

pkgname=python-i3configger
pkgver=0.6.0
pkgrel=1
pkgdesc='i3 config manipulation tool'
arch=('any')
url='http://oliver.bestwalter.de/i3configger/'
license=('MIT')
source=("https://pypi.io/packages/source/i/i3configger/i3configger-${pkgver}.tar.gz")
sha256sums=('72f812f46f580766ce5b6fa549c78362ed8cf545b3456211f2cbe905aeab392b')

build() {
  cd "$srcdir"/i3configger-$pkgver
  python setup.py build
}

package_python-i3configger() {
  # TODO needed 'python-inotify'
  depends=('python-setuptools' 'python-psutil' 'python-daemon')
  cd "$srcdir"/i3configger-$pkgver
  python setup.py install --root="$pkgdir" --optimize=1
  ln -s i3configger "$pkgdir"/usr/bin/i3configger
}
