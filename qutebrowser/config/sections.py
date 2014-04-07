# Copyright 2014 Florian Bruhin (The Compiler) <mail@qutebrowser.org>
#
# This file is part of qutebrowser.
#
# qutebrowser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# qutebrowser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with qutebrowser.  If not, see <http://www.gnu.org/licenses/>.

"""Setting sections used for qutebrowser."""

import logging
from collections import OrderedDict

import qutebrowser.config.conftypes as conftypes


class KeyValue:

    """Representation of a section with ordinary key-value mappings.

    This is a section which contains normal "key = value" pairs with a fixed
    set of keys.

    Attributes:
        values: An OrderedDict with key as index and value as value.
                key: string
                value: SettingValue
        descriptions: A dict with the description strings for the keys.

    """

    def __init__(self, *args):
        """Constructor.

        Args:
            *args: Key/Value pairs to set.
                   key: string
                   value: SettingValue

        """
        if args:
            self.descriptions = {}
            self.values = OrderedDict()
            for (k, settingval, desc) in args:
                self.values[k] = settingval
                self.descriptions[k] = desc

    def __getitem__(self, key):
        """Get the value for key.

        Args:
            key: The key to get a value for, as a string.

        Return:
            The value, as value class.

        """
        return self.values[key]

    def __setitem__(self, key, value):
        """Set the value for key.

        Args:
            key: The key to set the value for, as a string.
            value: The value to set, as a string

        """
        self.values[key].value = value

    def __iter__(self):
        """Iterate over all set values."""
        # FIXME using a custom iterator this could be done more efficiently.
        return self.values.__iter__()

    def __bool__(self):
        """Get boolean state."""
        return bool(self.values)

    def __contains__(self, key):
        """Return whether the section contains a given key."""
        return key in self.values

    def items(self):
        """Get dict item tuples."""
        return self.values.items()

    def from_cp(self, sect):
        """Initialize the values from a configparser section."""
        for k, v in sect.items():
            logging.debug("'{}' = '{}'".format(k, v))
            self.values[k].rawvalue = v


class ValueList:

    """This class represents a section with a list key-value settings.

    These are settings inside sections which don't have fixed keys, but instead
    have a dynamic list of "key = value" pairs, like keybindings or
    searchengines.

    They basically consist of two different SettingValues and have no defaults.

    Attributes:
        values: An OrderedDict with key as index and value as value.
        default: An OrderedDict with the default configuration as strings.
        types: A tuple for (keytype, valuetype)
        valdict: The "true value" dict.
        #descriptions: A dict with the description strings for the keys.
        #              Currently a global empty dict to be compatible with
        #              KeyValue section.

    """

    values = None
    default = None
    types = None
    #descriptions = {}

    def __init__(self, keytype, valtype, *defaults):
        """Wrap types over default values. Take care when overriding this."""
        self.types = (keytype, valtype)
        self.values = OrderedDict()
        self.default = OrderedDict(
            [(key, conftypes.SettingValue(valtype, value))
             for key, value in defaults])
        self.valdict = OrderedDict()

    def update_valdict(self):
        """Update the global "true" value dict."""
        self.valdict.clear()
        self.valdict.update(self.default)
        if self.values is not None:
            self.valdict.update(self.values)

    def __getitem__(self, key):
        """Get the value for key.

        Args:
            key: The key to get a value for, as a string.

        Return:
            The value, as value class.

        """
        try:
            return self.values[key]
        except KeyError:
            return self.default[key]

    def __iter__(self):
        """Iterate over all set values."""
        # FIXME using a custon iterator this could be done more efficiently
        self.update_valdict()
        return self.valdict.__iter__()

    def __bool__(self):
        """Get boolean state of section."""
        self.update_valdict()
        return bool(self.valdict)

    def __contains__(self, key):
        """Return whether the section contains a given key."""
        self.update_valdict()
        return key in self.valdict

    def items(self):
        """Get dict items."""
        self.update_valdict()
        return self.valdict.items()

    def from_cp(self, sect):
        """Initialize the values from a configparser section."""
        keytype = self.types[0]()
        valtype = self.types[1]()
        for k, v in sect.items():
            keytype.validate(k)
            valtype.validate(v)
            self.values[k] = conftypes.SettingValue(self.types[1], v)
