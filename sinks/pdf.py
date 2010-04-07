# -*- coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import pango
import pangocairo
import cairo

from src.hyphen import hyphenate
from src.registry import sinks, Sink

NAME = "pdf"
EXTENSION = "pdf"
DESCRIPTION = "generates PDF output"

def sink(metadata, file_obj):
    dpi_factor = 72 / 25.4
        
    paper_sizes = {"a4": (210.0, 297.0),
                   "a5": (148.5, 210.0),
                   "letter": (216.0, 279.0)}
    class PageManager(object):
        class MyLayout(object):
            def __init__(self, pdf_surface, position, satzspiegel, page_manager):
                cairo_context = cairo.Context(pdf_surface)
                self._position = position
                cairo_context.move_to(*position)
                pangocairo_context = pangocairo.CairoContext(cairo_context)
                pango_layout = pangocairo_context.create_layout()
                pango_layout.set_justify(True)
                pango_layout.set_spacing(1.5 * pango.SCALE)
                pango_layout.set_font_description(pango.FontDescription("serif normal 9"))
                pango_layout.set_width(int(pango.SCALE *  
                    (paper_sizes[meta_infos["paper_size"]][0] * dpi_factor -
                    satzspiegel[1] - satzspiegel[3])))
                self._cairo_context = cairo_context
                self._pangocairo_context = pangocairo_context
                self._pango_layout = pango_layout
                self._page_manager = page_manager
                self._markup = []
                
            def set_markup(self, text):
                self._pango_layout.set_markup(text)
                self._markup = [text]
                
            def add_markup(self, text):
                self._markup.append(text)
                self._pango_layout.set_markup(" ".join(self._markup).strip())
            
            @property
            def text(self):
                return self._pango_layout.get_text()
                
            @text.setter
            def text(self, text):
                self._pango_layout.set_text(text)
            
            @property
            def attributes(self):
                return self._pango_layout.get_attributes()
                
            @attributes.setter
            def attributes(self, attributes):
                self._pango_layout.set_attributes(attributes)
            
            @property
            def alignment(self):
                return self._pango_layout.get_alignment()
                
            @property
            def indent(self):
                return self._pango_layout.get_indent()
                
            @indent.setter
            def indent(self, value):
                return self._pango_layout.set_indent(value * pango.SCALE)
                
            @alignment.setter
            def alignment(self, value):
                self._pango_layout.set_alignment(value)
            
            @property
            def height(self):
                return (self._pango_layout.get_size()[1] + self._pango_layout.get_spacing()) / pango.SCALE
                
            @property
            def line_count(self):
                return self._pango_layout.get_line_count()
                
            def finish(self, break_after=True, show_page_number=True):
                # This should definitelly be implemented using
                # pango.Layout.set_height(), unfortunatelly the gtk python
                # bindings don't sport that method though it's in C (and
                # other bindings) for some time. Damn.
                if (break_after and self._page_manager.unused_height >= self.height) \
                or (not break_after and self._page_manager.unused_height >= self._page_manager.line_height * 2):
                    self._pangocairo_context.show_layout(self._pango_layout)
                    self._page_manager.used_height += self.height
                elif break_after:
                    rest_markup = []
                    i = 0
                    markup_list = self._markup
                    self.set_markup("")
                    backup = self._pango_layout.copy()
                    for markup in markup_list:
                        self.add_markup(markup)
                        if self._page_manager.unused_height >= self.height:
                            i += 1
                            backup = self._pango_layout.copy()
                        else:
                            rest_markup = markup_list[i:]
                    if rest_markup:
                        if not "".join(rest_markup).strip():
                            # don't start page with empty line(s)
                            return
                        self._pango_layout = backup
                        self._pangocairo_context.show_layout(backup)
                        self._page_manager.show_page(show_page_number)
                        self._pango_layout.set_markup("")
                        dummy_layout = self._page_manager.create_layout()
                        if self.alignment:
                            dummy_layout.alignment = self.alignment
                        dummy_layout.set_markup(" ".join(rest_markup).lstrip())
                        dummy_layout.finish()
                else:
                    self._page_manager.show_page(show_page_number)
                    dummy_layout = self._page_manager.create_layout()
                    if self.alignment:
                        dummy_layout.alignment = self.alignment
                    dummy_layout.set_markup(" ".join(self._markup).lstrip())
                    dummy_layout.finish()


        def __init__(self, meta_infos, file_obj):
            self.page_count = 1
            self.meta_infos = meta_infos
            self.width = paper_sizes[meta_infos["paper_size"]][0] * dpi_factor
            self.height = paper_sizes[meta_infos["paper_size"]][1] * dpi_factor
            self.pdf_surface = pdf_surface = cairo.PDFSurface(file_obj,self.width, self.height)
            self.current_page_left = False
            one_nineth = self.width / 9, self.height / 9
            if meta_infos["two_page"]:
                self.satzspiegel = one_nineth[1], one_nineth[0], one_nineth[1] * 2, one_nineth[0] * 2
            else:
                self.satzspiegel = one_nineth[1], one_nineth[0] * 1.5, one_nineth[1] * 2, one_nineth[0] * 1.5
            self._maximal_height = one_nineth[1] * 6
            self.one_nineth = one_nineth
            
            # get line_height
            temp_layout = self.MyLayout(self.pdf_surface, (0, 0), self.satzspiegel, self)
            temp_layout.text = "2341"
            temp_layout._pango_layout.set_spacing(2)
            self.line_height = temp_layout.height
            self._maximal_lines = int(one_nineth[1] * 6 / self.line_height * 2.54)
            self.used_height = 0
            if meta_infos["language"] is not None:
                self.hyphenator = hyphen.hyphenate(meta_infos["language"])
            else:
                self.hyphenator = None
            
        def create_layout(self):
            satzspiegel = self.satzspiegel
            if self.current_page_left:
                position = (satzspiegel[3], satzspiegel[0] + self.used_height)
            else:
                position = (satzspiegel[1], satzspiegel[0] + self.used_height)
            layout = self.MyLayout(self.pdf_surface, position, satzspiegel, self)
            return layout
            
        def create_title_layout(self):
            one_nineth = self.one_nineth
            satzspiegel = one_nineth[1], one_nineth[0] * 1.5, one_nineth[1] * 2, one_nineth[0] * 1.5
            position = (satzspiegel[3], satzspiegel[0])
            layout = self.MyLayout(self.pdf_surface, position, satzspiegel, self)
            layout.alignment = pango.ALIGN_CENTER
            return layout
        
        def _show_page_number(self):
            cairo_context = cairo.Context(self.pdf_surface)
            
            pangocairo_context = pangocairo.CairoContext(cairo_context)
            pango_layout = pangocairo_context.create_layout()
            pango_layout.set_markup("<span size='small'>" + str(self.page_count) + "</span>")
            width = pango_layout.get_size()[0]
            if self.current_page_left:
                pango_layout.set_alignment(pango.ALIGN_LEFT)
                cairo_context.move_to(self.satzspiegel[3],
                                      self.height - self.satzspiegel[2] + self.line_height * 2)
            else:
                pango_layout.set_alignment(pango.ALIGN_RIGHT)
                cairo_context.move_to(self.width - self.satzspiegel[3] - width / pango.SCALE,
                                      self.height - self.satzspiegel[2] + self.line_height * 2)
            pangocairo_context.show_layout(pango_layout)
        
        def show_page(self, show_page_number=True):
            if show_page_number:
                self._show_page_number()
            
            self.page_count += 1
            self.current_page_left = not self.current_page_left
            self.pdf_surface.show_page()
            self.used_height = 0
            
        def finish(self):
            self._show_page_number()
            self.pdf_surface.finish()
            
        @property
        def unused_height(self):
            return self._maximal_height - self.used_height

            
    print("starting sink '{0}' ...".format(NAME))
    try:
        meta_infos = {"paper_size": "a4",
                      "two_page": True,
                      "table_of_contents": False,
                      "language": None}
        
        state, event, value = (yield)
        data = intern(b"data")
        start = intern(b"start")
        end = intern(b"end")
                
        # Start
        while True:
            if state is not start:
                break
            state, event, value = (yield)
        
        # Header
        while state == b"head":
            if event == b"macro_data":
                option, macro_value = value
                meta_infos[option] = macro_value
            state, event, value = (yield)
        
        page_manager = PageManager(meta_infos, file_obj)
        
        # Title
        title_layout = None
        attribs = {"title": "", "author": "", "blocks": []}
        current_tag = ""
        while state in (b"title", b"title_body", b"title_block", b"title_value", b"title_tag"):
            if state == b"title":
                if event is start:
                    title = []
                elif event is data:
                    title.append(value)
                elif event is end:
                    attribs["title"] = " ".join(title)
                    del title
            elif state == b"title_tag":
                if event is start:
                    tag = []
                elif event is data:
                    tag.append(value)
                elif event is end:
                    current_tag = " ".join(tag)
            elif state == b"title_value":
                if event is start:
                    val = []
                elif event is data:
                    val.append(value)
                elif event is end:
                    attribs[current_tag] = " ".join(val)
                    del val
            elif state == b"title_block":
                if event is start:
                    block = []
                elif event is data:
                    block.append(value)
                elif event is end:
                    attribs["blocks"].append(" ".join(block))
                    del block
                    
            elif event == b"macro_data":
                # TODO
                continue
            state, event, value = (yield)
        else:
            if attribs["title"]:
                title_layout = page_manager.create_title_layout()
                markup = ""
                markup += "<span size='large'>" + attribs["author"] + "</span>\n"
                markup += "<span size='xx-large'>" + attribs["title"] + "</span>\n"
                for block in attribs["blocks"]:
                    markup += "<span style='oblique'>" + block + "</span>"
                title_layout.set_markup(markup)
                title_layout.finish()
                page_manager.show_page(show_page_number=False)
        
        while state in (b"cast", b"cast_body", b"cast_block",
                             b"actor_des", b"actor_dec"):
            state, event, value = (yield)
            # TODO
        
        current_dialog_line = ""
        while state is not end:
            if state == b"act":                
                if event is start:
                    act = []
                elif event is data:
                    act.append(value)
                elif event is end:
                    layout = page_manager.create_layout()
                    layout.alignment = pango.ALIGN_CENTER
                    layout.set_markup("<span size='x-large'>" + " ".join(act) + "</span>")
                    layout.finish(break_after=False)
            elif state == b"scene":                
                if event is start:
                    scene = []
                elif event is data:
                    scene.append(value)
                elif event is end:
                    layout = page_manager.create_layout()
                    layout.alignment = pango.ALIGN_CENTER
                    layout.set_markup("\n<span size='large'>" + " ".join(scene) + "</span>")
                    layout.finish(break_after=False)
            elif state == b"block":
                if event is start:
                    layout = page_manager.create_layout()
                elif event is data:
                    layout.add_markup("<span style='oblique'>" + value + "</span>")
                elif event is end:
                    layout.finish()
            elif state == b"empty_line":
                if event is end:
                    layout = page_manager.create_layout()
                    layout.text = ""
                    layout.finish()
            elif state == b"actor":
                if event is start:
                    dialog_layout = page_manager.create_layout()
                    dialog_layout.indent = -20
                elif event is data:
                    dialog_layout.add_markup("<span weight='bold'>" + value + "</span> ")
                elif event is end:
                    pass
            elif state == b"dialog":
                if event is start:
                    pass
                elif event is data:
                    dialog_layout.add_markup(value)
                elif event is end:
                    dialog_layout.finish()
            elif state == b"inline_dir":
                if event is start:
                    pass
                elif event is data:
                     dialog_layout.add_markup("<span style='oblique'>" + value + "</span>")
                elif event is end:
                    pass
                    
            state, event, value = (yield)

        page_manager.finish()

    except GeneratorExit:
        pass
    finally:
        print("stopped sink '{0}'".format(NAME))

sinks["pdf"] = Sink("pdf", "generates PDF output", sink)
