import sys; sys.path.insert(0,'api')
import index

with index.app.test_client() as c:
    r = c.get('/assessor')
    html = r.data.decode('utf-8')
    idx = html.find('id="perfil"')
    print("SELECT HTML:", html[idx:idx+400])
    print()
    print("onchange present:", "onchange" in html[idx:idx+400])
