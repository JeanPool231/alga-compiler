"""Renderiza la guía Markdown en PDF Unicode usando Cairo/Pango del sistema.

Linux: necesita libcairo, libpango y libpangocairo, sin paquetes Python externos.
Los separadores --- de la fuente establecen los saltos de página explícitos.
"""
import ctypes as C
from ctypes.util import find_library
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def library(name):
    filename = find_library(name)
    if filename is None:
        raise SystemExit(f'Falta la biblioteca de sistema {name}; el PDF generado está en entregables/.')
    return C.CDLL(filename)


def bind(lib, name, result, *args):
    fn = getattr(lib, name)
    fn.restype, fn.argtypes = result, args
    return fn


def main():
    cairo, pango, pc, gobject = map(library, ['cairo', 'pango-1.0', 'pangocairo-1.0', 'gobject-2.0'])
    ptr, d, integer, char = C.c_void_p, C.c_double, C.c_int, C.c_char_p
    pdf = bind(cairo, 'cairo_pdf_surface_create', ptr, char, d, d)
    create = bind(cairo, 'cairo_create', ptr, ptr)
    rgb = bind(cairo, 'cairo_set_source_rgb', None, ptr, d, d, d)
    rectangle = bind(cairo, 'cairo_rectangle', None, ptr, d, d, d, d)
    fill = bind(cairo, 'cairo_fill', None, ptr)
    move = bind(cairo, 'cairo_move_to', None, ptr, d, d)
    showpage = bind(cairo, 'cairo_show_page', None, ptr)
    finish = bind(cairo, 'cairo_surface_finish', None, ptr)
    status = bind(cairo, 'cairo_surface_status', integer, ptr)
    destroy = bind(cairo, 'cairo_destroy', None, ptr)
    surface_destroy = bind(cairo, 'cairo_surface_destroy', None, ptr)
    layout_create = bind(pc, 'pango_cairo_create_layout', ptr, ptr)
    layout_show = bind(pc, 'pango_cairo_show_layout', None, ptr, ptr)
    layout_text = bind(pango, 'pango_layout_set_text', None, ptr, char, integer)
    layout_width = bind(pango, 'pango_layout_set_width', None, ptr, integer)
    layout_wrap = bind(pango, 'pango_layout_set_wrap', None, ptr, integer)
    layout_size = bind(pango, 'pango_layout_get_size', None, ptr, C.POINTER(integer), C.POINTER(integer))
    font_new = bind(pango, 'pango_font_description_from_string', ptr, char)
    font_size = bind(pango, 'pango_font_description_set_absolute_size', None, ptr, d)
    font_set = bind(pango, 'pango_layout_set_font_description', None, ptr, ptr)
    font_free = bind(pango, 'pango_font_description_free', None, ptr)
    unref = bind(gobject, 'g_object_unref', None, ptr)
    out = ROOT / 'entregables/12_cambios_docx_iteraciones.pdf'
    surface = pdf(str(out).encode(), 595.28, 841.89)
    context = create(surface)
    layout = layout_create(context)
    layout_wrap(layout, 2)  # WORD_CHAR

    def draw(text, x, y, size=10.5, width=507, font='sans', color=(0.13, 0.18, 0.23)):
        descriptor = font_new(font.encode())
        font_size(descriptor, size * 1024)
        font_set(layout, descriptor)
        font_free(descriptor)
        layout_width(layout, int(width * 1024))
        layout_text(layout, text.encode('utf-8'), -1)
        w, h = integer(), integer()
        layout_size(layout, C.byref(w), C.byref(h))
        move(context, x, y)
        rgb(context, *color)
        layout_show(context, layout)
        return h.value / 1024

    pages = (ROOT / 'docs/12_cambios_docx_iteraciones.md').read_text(encoding='utf-8').split('\n---\n')
    for number, page in enumerate(pages, 1):
        rgb(context, 0.05, 0.29, 0.36)
        rectangle(context, 44, 32, 507, 4)
        fill(context)
        y = 49
        code = False
        lines = page.strip().splitlines()
        index = 0
        while index < len(lines):
            line = lines[index]
            index += 1
            if line.startswith('```'):
                code = not code
                y += 4
                continue
            if not line.strip():
                y += 5
                continue
            if code:
                height = draw(line, 49, y, 9, 497, 'monospace')
            elif line.startswith('# '):
                height = draw(line[2:], 44, y, 18, font='sans bold', color=(0.05, 0.29, 0.36))
                height += 10
            elif line.startswith('## '):
                height = draw(line[3:], 44, y, 12, font='sans bold')
                height += 4
            else:
                while index < len(lines) and lines[index].strip() and not lines[index].startswith(('#', '```')):
                    line += ' ' + lines[index].strip()
                    index += 1
                line = re.sub(r'`([^`]+)`', r'\1', line)
                height = draw(line, 44, y)
                height += 4
            y += height
            if y > 784:
                raise RuntimeError(f'Página {number} excede el área de contenido: y={y:.1f}')
        draw('ALGA · Guía de actualización del DOCX · Hito 1', 44, 807, 8.5, color=(0.4, 0.45, 0.5))
        draw(f'{number} / {len(pages)}', 509, 807, 8.5, width=50)
        showpage(context)
    unref(layout)
    destroy(context)
    finish(surface)
    code = status(surface)
    surface_destroy(surface)
    if code:
        raise RuntimeError(f'Error Cairo {code}')
    print(f'Guía PDF: {out.name}; {len(pages)} páginas, texto Unicode seleccionable.')


if __name__ == '__main__':
    main()
