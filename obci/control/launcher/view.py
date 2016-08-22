#!/usr/bin/python
# -*- coding: utf-8 -*-


class OBCIView(object):

    def view(self, msg, where=None):
        """
        Abstract method for printing data in launcher messages.
        """
        if msg is None:
            msg = str(msg)
        if isinstance(msg, str):
            formatter = self._view_str
        else:
            formatter = self.view_raw

            try:
                formatter = getattr(self, "_view_" + msg.type)
            except AttributeError:
                pass

        result = formatter(msg)
        self._show(result, where)

    def view_raw(self, msg, where=None):
        raise NotImplementedError()

    def format_default(self, msg):
        raise NotImplementedError()

    def _view_str(self, msg):
        raise NotImplementedError()

    def _show(self, formatted_msg, where=None):
        raise NotImplementedError()


class OBCIViewText(OBCIView):

    def _show(self, formatted_msg, where=None):
        print(formatted_msg)

    def format_default(self, msg):
        lst = []
        self._format_msg(msg.dict(), lst, 0)

        return ''.join(lst)

    def view_raw(self, msg, where=None):
        print(msg.raw())

    def _format_msg(self, msg, lst, depth):
        if isinstance(msg, dict):
            for key, val in msg.items():
                lst += ['\n', '   ' * depth, key, ':  ']
                self._format_msg(val, lst, depth + 1)
        elif isinstance(msg, list):
            for elt in msg:
                self._format_msg(elt, lst, depth + 2)
                lst += ['\n', '   ' * (depth + 3)]
        else:
            lst += [str(msg)]

    def _view_running_experiments(self, msg):
        return self.format_default(msg)

    def _view_str(self, msg):
        return msg

    def _view_tail(self, msg):
        output = ''
        for line in msg.txt:
            output += line
        return output
