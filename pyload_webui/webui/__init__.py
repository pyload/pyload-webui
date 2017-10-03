# -*- coding: utf-8 -*-
# @author: RaNaN, vuolter
#      ____________
#   _ /       |    \ ___________ _ _______________ _ ___ _______________
#  /  |    ___/    |   _ __ _  _| |   ___  __ _ __| |   \\    ___  ___ _\
# /   \___/  ______/  | '_ \ || | |__/ _ \/ _` / _` |    \\  / _ \/ _ `/ \
# \       |   o|      | .__/\_, |____\___/\__,_\__,_|    // /_//_/\_, /  /
#  \______\    /______|_|___|__/________________________//______ /___/__/
#          \  /
#           \/

from __future__ import absolute_import, unicode_literals

from future import standard_library
standard_library.install_aliases()
import locale

# from .__about__ import __package__
# from pkg_resources import resource_filename
# from pyload.utils.misc import install_translation

locale.setlocale(locale.LC_ALL, '')
# install_translation('webui', pkg_resources.resource_filename(__package__, 'locale'))
