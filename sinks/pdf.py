# -*- coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import pango
import pangocairo
import cairo

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
                pango_layout.set_spacing(2 * pango.SCALE)
                pango_layout.set_font_description(pango.FontDescription("serif normal 10"))
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
                
            @property
            def block_indent(self):
                pass # TODO
                
            @block_indent.setter
            def block_indent(self, value):
                return self._cairo_context.move_to(self._position[0] + value, self._position[1])
                
            @alignment.setter
            def alignment(self, value):
                self._pango_layout.set_alignment(value)
            
            @property
            def height(self):
                return self._pango_layout.get_size()[1] / pango.SCALE + self._pango_layout.get_spacing() / pango.SCALE
                
            @property
            def line_count(self):
                return self._pango_layout.get_line_count()
                
            def finish(self, break_after=True, show_page_number=True):
                # This should definitelly be implemented using
                # pango.Layout.set_height(), unfortunatelly the gtk python
                # bindings don't sport that method though it's in C (and
                # other bindings) for some time. Damn.
                if (break_after and self._page_manager.unused_height >= 0) \
                or (not break_after and self._page_manager.unused_height >= self._page_manager.line_height * 2):
                    
                    self._pangocairo_context.show_layout(self._pango_layout)
                    self._page_manager.lines_on_page += self.line_count
                elif break_after:
                    rest_markup = []
                    i = 0
                    markup_list = self._markup
                    self.set_markup("")
                    backup = self._pango_layout.copy()
                    for markup in markup_list:
                        self.add_markup(markup)
                        if self._page_manager.unused_height >= 0:
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
            self.pdf_surface = pdf_surface = cairo.PDFSurface(file_obj,
                   paper_sizes[meta_infos["paper_size"]][0] * dpi_factor,
                   paper_sizes[meta_infos["paper_size"]][1] * dpi_factor)
            self._on_page = []
            self.current_page_left = False
            one_nineth = paper_sizes[meta_infos["paper_size"]][0] / 9 * dpi_factor, paper_sizes[meta_infos["paper_size"]][1] / 9 * dpi_factor
            if meta_infos["two_page"]:
                self.satzspiegel = one_nineth[1], one_nineth[0], one_nineth[1] * 2, one_nineth[0] * 2
            else:
                self.satzspiegel = one_nineth[1], one_nineth[0] * 1.5, one_nineth[1] * 2, one_nineth[0] * 1.5
            self._maximal_height = one_nineth[1] * 6
            self.one_nineth = one_nineth
            self.lines_on_page = 0
            
            # get line_height
            temp_layout = self.MyLayout(self.pdf_surface, (0, 0), self.satzspiegel, self)
            temp_layout.text = "2341"
            temp_layout._pango_layout.set_spacing(2)
            self.line_height = temp_layout.height
            self._maximal_lines = int(one_nineth[1] * 6 / self.line_height * 2.54)
            
        def create_layout(self):
            satzspiegel = self.satzspiegel
            if self.current_page_left:
                position = (satzspiegel[3], satzspiegel[0] + self.offset)
            else:
                position = (satzspiegel[1], satzspiegel[0] + self.offset)
            layout = self.MyLayout(self.pdf_surface, position, satzspiegel, self)
            self._on_page.append(layout)
            return layout
            
        def create_title_layout(self):
            one_nineth = self.one_nineth
            satzspiegel = one_nineth[1], one_nineth[0] * 1.5, one_nineth[1] * 2, one_nineth[0] * 1.5
            position = (satzspiegel[3], satzspiegel[0])
            layout = self.MyLayout(self.pdf_surface, position, satzspiegel, self)
            layout.alignment = pango.ALIGN_CENTER
            self._on_page.append(layout)
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
                                      paper_sizes[meta_infos["paper_size"]][1] * dpi_factor - self.satzspiegel[2] + self.line_height * 2)
            else:
                pango_layout.set_alignment(pango.ALIGN_RIGHT)
                cairo_context.move_to(paper_sizes[meta_infos["paper_size"]][0] * dpi_factor - self.satzspiegel[3] - width / pango.SCALE,
                                      paper_sizes[meta_infos["paper_size"]][1] * dpi_factor - self.satzspiegel[2] + self.line_height * 2)
            pangocairo_context.show_layout(pango_layout)
        
        def show_page(self, show_page_number=True):
            if show_page_number:
                self._show_page_number()
            
            self.page_count += 1
            self.current_page_left = not self.current_page_left
            self.pdf_surface.show_page()
            self.lines_on_page = 0
            self._on_page = []
            
        def finish(self):
            self._show_page_number()
            self.pdf_surface.finish()
            
        @property
        def offset(self):
            return sum([on_page_layout.height for on_page_layout in self._on_page])
        
        @property
        def line_count(self):
            return sum([on_page_layout.line_count for on_page_layout in self._on_page])
            
        @property
        def unused_height(self):
            return self._maximal_height - self.offset

            
    print("starting sink '{0}' ...".format(NAME))
    try:
        meta_infos = {"paper_size": "a4", "two_page": True, "table_of_contents": False}
        
        state, event, value = (yield)
                
        # Start
        while True:
            if state != "start":
                break
            state, event, value = (yield)
        
        # Header
        while state == "head":
            if event == "macro_data":
                option, macro_value = value
                meta_infos[option] = macro_value
            state, event, value = (yield)
        
        page_manager = PageManager(meta_infos, file_obj)
        
        # Title
        title_layout = None
        attribs = {"title": "", "author": "", "blocks": []}
        current_tag = ""
        while state in ("title", "title_body", "title_block", "title_value", "title_tag"):
            if state == "title":
                if event == "start":
                    title = []
                elif event == "data":
                    title.append(value)
                elif event == "end":
                    attribs["title"] = " ".join(title)
                    del title
            elif state == "title_tag":
                if event == "start":
                    tag = []
                elif event == "data":
                    tag.append(value)
                elif event == "end":
                    current_tag = " ".join(tag)
            elif state == "title_value":
                if event == "start":
                    val = []
                elif event == "data":
                    val.append(value)
                elif event == "end":
                    attribs[current_tag] = " ".join(val)
                    del val
            elif state == "title_block":
                if event == "start":
                    block = []
                elif event == "data":
                    block.append(value)
                elif event == "end":
                    attribs["blocks"].append(" ".join(block))
                    del block
                    
            elif event == "macro_data":
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
        
        while state in ("cast", "cast_body", "cast_block",
                             "actor_des", "actor_dec"):
            state, event, value = (yield)
            # TODO
        
        current_dialog_line = ""
        while state != "end":
            if state == "act":                
                if event == "start":
                    act = []
                elif event == "data":
                    act.append(value)
                elif event == "end":
                    layout = page_manager.create_layout()
                    layout.alignment = pango.ALIGN_CENTER
                    layout.set_markup("<span size='x-large'>" + " ".join(act) + "</span>")
                    layout.finish(break_after=False)
            elif state == "scene":                
                if event == "start":
                    scene = []
                elif event == "data":
                    scene.append(value)
                elif event == "end":
                    layout = page_manager.create_layout()
                    layout.alignment = pango.ALIGN_CENTER
                    layout.set_markup("\n<span size='large'>" + " ".join(scene) + "</span>")
                    layout.finish(break_after=False)
            elif state == "block":
                if event == "start":
                    layout = page_manager.create_layout()
                elif event == "data":
                    layout.add_markup("<span style='oblique'>" + value + "</span>")
                elif event == "end":
                    layout.finish()
            elif state == "empty_line":
                if event == "end":
                    layout = page_manager.create_layout()
                    layout.text = ""
                    layout.finish()
            elif state == "actor":
                if event == "start":
                    dialog_layout = page_manager.create_layout()
                    dialog_layout.indent = -20
                elif event == "data":
                    dialog_layout.add_markup("<span weight='bold'>" + value + "</span> ")
                elif event == "end":
                    pass
            elif state == "dialog":
                if event == "start":
                    #dialog = []
                    pass
                elif event == "data":
                    #dialog.append(value)
                    dialog_layout.add_markup(value)
                elif event == "end":
                    dialog_layout.finish()
            elif state == "inline_dir":
                if event == "start":
                    pass
                elif event == "data":
                     dialog_layout.add_markup("<span style='oblique'>" + value + "</span>")
                elif event == "end":
                    pass
                    
            state, event, value = (yield)

        page_manager.finish()

    except GeneratorExit:
        pass
    finally:
        print("stopped sink '{0}'".format(NAME))
