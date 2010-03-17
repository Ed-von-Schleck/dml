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
    class LayoutManager(object):
        class MyLayout(object):
            def __init__(self, pdf_surface, position, satzspiegel):
                self.page_count = 0
                cairo_context = cairo.Context(pdf_surface)
                cairo_context.move_to(*position)
                pangocairo_context = pangocairo.CairoContext(cairo_context)
                pango_layout = pangocairo_context.create_layout()
                pango_layout.set_justify(True)
                pango_layout.set_font_description(pango.FontDescription("serif normal 10"))
                pango_layout.set_width(int(pango.SCALE *
                    (paper_sizes[meta_infos["paper_size"]][0] -
                    satzspiegel[1] - satzspiegel[3]) * dpi_factor))
                self.cairo_context = cairo_context
                self.pangocairo_context = pangocairo_context
                self.pango_layout = pango_layout
                
            def set_markup(self, text):
                self.pango_layout.set_markup(text)
                
            def set_text(self, text):
                self.pango_layout.set_text(text)
            
            @property
            def alignment(self):
                return pango_layout.get_alignment()
                
            @alignment.setter(self, value):
                pango_layout.set_alignment(value)
            
            def get_height(self):
                return self.pango_layout.get_size()[1] / pango.SCALE
                
            def finish(self):
                self.pangocairo_context.show_layout(self.pango_layout)
                
        def __init__(self, meta_infos, file_obj):
            self.meta_infos = meta_infos
            self.pdf_surface = pdf_surface = cairo.PDFSurface(file_obj,
                   paper_sizes[meta_infos["paper_size"]][0] * dpi_factor,
                   paper_sizes[meta_infos["paper_size"]][1] * dpi_factor)
            self._on_page = []
            self.current_page_left = True
            one_nineth = paper_sizes[meta_infos["paper_size"]][0] / 9, paper_sizes[meta_infos["paper_size"]][1] / 9
            if meta_infos["two_page"]:
                self.satzspiegel = one_nineth[1], one_nineth[0], one_nineth[1] * 2, one_nineth[0] * 2
            else:
                self.satzspiegel = one_nineth[1], one_nineth[0] * 1.5, one_nineth[1] * 2, one_nineth[0] * 1.5
            self.one_nineth = one_nineth
            
        def create_layout(self):
            offset = sum([on_page_layout.get_height() for on_page_layout in self._on_page])
            if self.current_page_left:
                position = (dpi_factor * self.satzspiegel[3], dpi_factor * self.satzspiegel[0] + offset)
            else:
                position = (dpi_factor * self.satzspiegel[1], dpi_factor * self.satzspiegel[0] + offset)
            self.current_page_left = not self.current_page_left
            layout = self.MyLayout(self.pdf_surface, position, self.satzspiegel)
            self._on_page.append(layout)
            return layout
            
        def create_title_layout(self):
            one_nineth = self.one_nineth
            satzspiegel = one_nineth[1], one_nineth[0] * 1.5, one_nineth[1] * 2, one_nineth[0] * 1.5
            position = (dpi_factor * satzspiegel[3], dpi_factor * satzspiegel[0])
            layout = self.MyLayout(self.pdf_surface, position, satzspiegel)
            layout.alignment = pango.ALIGN_CENTER
            self._on_page.append(layout)
            return layout
        
        def show_page(self):
            self.page_count += 1
            self.pdf_surface.show_page()
            self._on_page = []
            
        def finish(self):
            self.pdf_surface.finish()
        
            
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
            
        layout_manager = LayoutManager(meta_infos, file_obj)
        
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
                title_layout = layout_manager.create_title_layout()
                markup = ""
                markup += "<span size='large'>" + attribs["author"] + "</span>\n"
                markup += "<span size='xx-large'>" + attribs["title"] + "</span>\n"
                for block in attribs["blocks"]:
                    markup += "\n<span style='oblique'>" + block + "</span>\n"
                title_layout.set_markup(markup)
                title_layout.finish()
        
        while state in ("cast", "cast_body", "cast_block",
                             "actor_des", "actor_dec"):
            state, event, value = (yield)
            # TODO
        
        while state != "end":
            if state == "act":
                if event == "start":
                    act = []
                elif event == "data":
                    act.append(value)
                elif event == "end":
                    layout = layout_manager.create_title_layout()
                    layout.alignment = pango.ALIGN_CENTER
                
                
        
        layout_manager.show_page()
        layout_manager.finish()

    except GeneratorExit:
        pass
    finally:
        print("stopped sink '{0}'".format(NAME))
