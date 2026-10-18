from pathlib import Path
import zipfile,json,xml.etree.ElementTree as ET

src=Path(r'D:\微信\浏览记录\xwechat_files\wxid_3aupvd7hoj0q22_8e0b\msg\file\2026-10\02 MCP Server工厂与连接器自测报告.docx')
out=Path(r'D:\agent学习\report_revision')
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing','v':'urn:schemas-microsoft-com:vml'}
def txt(el): return ''.join(e.text or '' for e in el.findall('.//w:t',ns))
def images(el):
    return [{'rid':b.get('{'+ns['r']+'}embed'),'target':rels.get(b.get('{'+ns['r']+'}embed'))} for b in el.findall('.//a:blip',ns)]
with zipfile.ZipFile(src) as z:
    rels={e.get('Id'):e.get('Target') for e in ET.fromstring(z.read('word/_rels/document.xml.rels'))}
    root=ET.fromstring(z.read('word/document.xml'))
    blocks=[]
    lines=[]
    for bi,el in enumerate(root.find('w:body',ns)):
        tag=el.tag.split('}')[-1]
        block={'index':bi,'type':tag}
        if tag=='p':
            block.update(text=txt(el),images=images(el))
            lines.append(f'BLOCK {bi} PARA: '+txt(el))
            if block['images']: lines.append('  IMAGES '+json.dumps(block['images'],ensure_ascii=False))
        elif tag=='tbl':
            rows=[]
            for ri,row in enumerate(el.findall('w:tr',ns)):
                cells=[]
                for ci,cell in enumerate(row.findall('w:tc',ns)):
                    d={'row':ri,'col':ci,'text':txt(cell),'images':images(cell),'paragraphs':[txt(p) for p in cell.findall('w:p',ns)]}
                    cells.append(d)
                    lines.append(f'BLOCK {bi} ROW {ri} CELL {ci}: '+d['text'])
                    if d['images']:lines.append('  IMAGES '+json.dumps(d['images'],ensure_ascii=False))
                rows.append(cells)
            block['rows']=rows
        blocks.append(block)
    (out/'document_structure.json').write_text(json.dumps({'source':str(src),'relationships':rels,'blocks':blocks},ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'document_text.txt').write_text('\n'.join(lines),encoding='utf-8')
    (out/'document.xml').write_bytes(z.read('word/document.xml'))
    for name in z.namelist():
        if name.startswith('word/media/'):
            dest=out/'original_media'/Path(name).name
            dest.parent.mkdir(exist_ok=True)
            dest.write_bytes(z.read(name))
print(json.dumps({'blocks':len(blocks),'tables':sum(b['type']=='tbl' for b in blocks),'media':len(list((out/'original_media').iterdir()))},ensure_ascii=False))
