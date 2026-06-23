import sys; sys.path.insert(0,'api')
import index

with index.app.test_client() as c:
    r = c.get('/assessor')
    html = r.data.decode('utf-8')

    print('setupDrop presente:', 'setupDrop' in html)
    print('btn-proxima-etapa-wrap presente:', 'btn-proxima-etapa-wrap' in html)
    print('handleFile presente:', 'handleFile' in html)
    print('step2-wrapper presente:', 'step2-wrapper' in html)

    idx_drop1 = html.find('id="drop1"')
    idx_fn = html.find('function setupDrop')
    idx_call = html.find('setupDrop("drop1"')
    print('idx drop1:', idx_drop1)
    print('idx setupDrop fn:', idx_fn)
    print('idx setupDrop call:', idx_call)
    print('drop1 antes do script?', idx_drop1 < idx_fn)

    # Mostra trecho ao redor do setupDrop call
    if idx_call > 0:
        print('\n--- contexto setupDrop call ---')
        print(html[idx_call-50:idx_call+200])

    # Verifica se btn-proxima-etapa-wrap está dentro do card
    idx_btn = html.find('btn-proxima-etapa-wrap')
    if idx_btn > 0:
        print('\n--- contexto btn-proxima-etapa-wrap ---')
        print(html[idx_btn-100:idx_btn+300])
