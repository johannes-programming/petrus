from petrus._core.calcs.Calc import Calc


class Block(Calc):
    def _calc_text(self):
        keys = "heading overview installation license links credits".split()
        blocks = []
        for k in keys:
            b = getattr(self, k)
            if b is None:
                continue
            b = b.strip("\n")
            blocks.append(b)
        ans = "\n\n".join(blocks)
        return ans

    def _calc_heading(self):
        n = self.prog.project.name
        l = "=" * len(n)
        ans = "%s\n%s\n%s" % (l, n, l)
        return ans

    def _calc_overview(self):
        d = str(self.prog.project.description)
        if not d:
            return None
        lines = self.ftitle("Overview")
        lines += str(d)
        return lines

    def _calc_installation(self):
        name = self.prog.project.name
        phrase = "To install %s, you can use `pip`. Open your terminal and run:"
        phrase %= name
        codestart = ".. code-block:: bash"
        codeline = "    pip install %s" % name
        lines = self.ftitle("Installation")
        lines += phrase
        lines += "\n" * 2
        lines += codestart
        lines += "\n" * 2
        lines += codeline
        return lines

    def _calc_license(self):
        mit = "License :: OSI Approved :: MIT License"
        classifiers = self.prog.project.classifiers
        if type(classifiers) is not list:
            return None
        if mit not in classifiers:
            return None
        lines = self.ftitle("License")
        lines += "This project is licensed under the MIT License."
        return lines

    def _calc_links(self):
        urls = self.prog.project.urls
        if type(urls) is not dict:
            return None
        if len(urls) == 0:
            return None
        lines = self.ftitle("Links")
        for i in urls.items():
            lines += "* `%s <%s>`_\n" % i
        return lines

    def _calc_credits(self):
        n, e = self.prog.author
        lines = self.ftitle("Credits")
        if n != "":
            lines += "- Author: %s\n" % n
        if e != "":
            lines += "- Email: %s\n" % e
        if n + e != "":
            lines += "\n"
        pn = self.prog.project.name
        lines += "Thank you for using %s!" % pn
        return lines

    @staticmethod
    def ftitle(value, /, lining="-"):
        value = str(value)
        lining = str(lining)
        lining *= len(value)
        ans = "%s\n%s\n\n" % (value, lining)
        return ans
