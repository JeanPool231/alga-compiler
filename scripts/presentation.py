"""Genera una presentación PDF autocontenida sin dependencias adicionales."""
import json
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parents[1]


def literal(text):
    raw = text.encode('cp1252')
    return b'(' + raw.replace(b'\\', b'\\\\').replace(b'(', b'\\(').replace(b')', b'\\)') + b')'


def make_pdf(slides):
    objects = [b'', b'',
               b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>',
               b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>']
    pages = []
    for number, slide in enumerate(slides, 1):
        stream = [b'0.035 0.075 0.13 rg 0 0 960 540 re f',
                  b'0.16 0.80 0.69 rg 48 478 58 5 re f']

        def text(x, y, size, value, bold=False, color=b'0.91 0.94 0.97'):
            stream.append(color + b' rg BT /' + (b'F2' if bold else b'F1') +
                          f' {size} Tf {x} {y} Td '.encode() + literal(value) + b' Tj ET')

        text(48, 425, 38, slide['titulo'], True)
        text(48, 390, 16, slide['subtitulo'], color=b'0.39 0.84 0.77')
        y = 333
        for line in slide['lineas']:
            for wrapped in textwrap.wrap(line, width=83):
                text(54, y, 18, wrapped)
                y -= 26
            y -= 10
        if y < 62:
            raise ValueError(f'Contenido excede diapositiva {number}')
        for i, line in enumerate(textwrap.wrap(slide['pie'], width=115)):
            text(48, 40 - i * 14, 11, line, color=b'0.61 0.70 0.79')
        text(880, 40, 12, f'{number:02}')
        content = b'\n'.join(stream)
        content_id = len(objects) + 1
        objects.append(b'<< /Length ' + str(len(content)).encode() + b' >>\nstream\n' + content + b'\nendstream')
        page_id = len(objects) + 1
        objects.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 960 540] /Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents {content_id} 0 R >>'.encode())
        pages.append(page_id)
    objects[0] = b'<< /Type /Catalog /Pages 2 0 R >>'
    objects[1] = ('<< /Type /Pages /Count ' + str(len(pages)) + ' /Kids [' +
                  ' '.join(f'{p} 0 R' for p in pages) + '] >>').encode()
    output = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(output))
        output.extend(f'{i} 0 obj\n'.encode() + obj + b'\nendobj\n')
    xref = len(output)
    output.extend(f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode())
    for offset in offsets[1:]:
        output.extend(f'{offset:010} 00000 n \n'.encode())
    output.extend(f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode())
    return output


if __name__ == '__main__':
    slides = json.loads((ROOT / 'entregables/09_presentacion.json').read_text(encoding='utf-8'))
    destination = ROOT / 'entregables/09_presentacion.pdf'
    destination.write_bytes(make_pdf(slides))
    print(f'Presentación creada: {destination.name} ({len(slides)} diapositivas)')
