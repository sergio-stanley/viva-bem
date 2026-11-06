"""Ponte com o navegador (pygbag): detecta tela de toque e mostra um formulário HTML no celular.

No celular, o Pygame desenha tudo num <canvas> e o teclado do aparelho não abre. Por isso, só na
tela de dados, criamos campos HTML de verdade por cima do jogo; ao tocar neles o teclado do próprio
celular aparece (numérico em idade/altura/peso).
"""
import json
import sys

NO_NAVEGADOR = sys.platform == "emscripten"
if NO_NAVEGADOR:
    import platform     # no pygbag: acesso a window/document do navegador


def eh_toque() -> bool:
    """True em celular/tablet (tela de toque). Sempre False fora do navegador."""
    if not NO_NAVEGADOR:
        return False
    try:
        return bool(platform.window.matchMedia("(pointer: coarse)").matches)
    except Exception:
        return False


def js_texto(texto: str) -> str:
    """Literal de string JavaScript só com ASCII (acentos viram \\uXXXX)."""
    return json.dumps(texto, ensure_ascii=True)


_CSS = """
#vb-form{position:fixed;inset:0;z-index:9999;overflow:auto;box-sizing:border-box;padding:28px 22px;
  background:radial-gradient(circle at 85% 0%,#0f4c5c 0%,#07161f 65%);color:#e8f6f4;
  font-family:Nunito,system-ui,-apple-system,"Segoe UI",sans-serif}
#vb-form h1{color:#2dd4bf;font-size:30px;margin:8px 0 4px;font-weight:800}
#vb-form p{color:#8fb5bd;font-size:15px;margin:0 0 22px}
#vb-form label{display:block;color:#8fb5bd;font-size:15px;margin:0 0 6px}
#vb-form input{display:block;width:100%;box-sizing:border-box;font-size:18px;padding:13px 14px;
  margin:0 0 16px;background:#07161f;color:#e8f6f4;border:2px solid #1f4a5e;border-radius:12px;outline:none}
#vb-form input:focus{border-color:#2dd4bf}
#vb-form .linha{display:flex;gap:10px}
#vb-form .linha>div{flex:1;min-width:0}
#vb-erro{color:#facc15;font-size:15px;min-height:20px;margin:0 0 14px}
#vb-form button{display:block;width:100%;font-size:19px;font-weight:800;padding:16px;border-radius:14px;
  margin:0 0 12px;border:2px solid #1f4a5e;background:#0e2633;color:#e8f6f4}
#vb-form button.prim{background:#2dd4bf;border-color:#2dd4bf;color:#07161f}
"""


def _campo_num(id_, rotulo):
    return (f'<div><label for="{id_}">{rotulo}</label>'
            f'<input id="{id_}" inputmode="numeric" pattern="[0-9]*" maxlength="3" autocomplete="off"></div>')


def html_formulario(erro: str = "") -> str:
    return (
        f"<style>{_CSS}</style>"
        '<form id="vb-f" novalidate onsubmit="window.vb_acao=\'ok\';return false;">'
        "<h1>Antes de começar</h1>"
        "<p>Seus dados não são guardados — servem só para o resultado.</p>"
        '<label for="vb-nome">Nome (opcional)</label>'
        '<input id="vb-nome" maxlength="20" autocomplete="off">'
        '<div class="linha">'
        + _campo_num("vb-idade", "Idade (anos)")
        + _campo_num("vb-altura", "Altura (cm)")
        + _campo_num("vb-peso", "Peso (kg)")
        + "</div>"
        f'<div id="vb-erro">{erro}</div>'
        '<button id="vb-ok" class="prim" type="submit">Continuar ›</button>'
        '<button id="vb-voltar" type="button" onclick="window.vb_acao=\'voltar\'">Voltar</button>'
        "</form>"
    )


def js_abrir(erro: str = "") -> str:
    return ("(function(){var v=document.getElementById('vb-form'); if(v) v.remove();"
            "window.vb_acao='';var d=document.createElement('div');d.id='vb-form';"
            f"d.innerHTML={js_texto(html_formulario(erro))};"
            # o SDL escuta o teclado na página toda e "cancela" as teclas: seguramos aqui antes
            "['keydown','keypress','keyup'].forEach(function(t){"
            "d.addEventListener(t,function(e){e.stopPropagation();},false);});"
            "document.body.appendChild(d);})();")


_JS_FECHAR = ("(function(){var a=document.activeElement; if(a&&a.blur) a.blur();"
              "var f=document.getElementById('vb-form'); if(f) f.remove(); window.vb_acao='';})();")


class FormularioWeb:
    """Formulário HTML sobre o canvas. Mesma interface usada pelos testes (FormularioFalso)."""

    def _eval(self, js):
        return platform.window.eval(js)

    def abrir(self, erro: str = ""):
        self._eval(js_abrir(erro))

    def acao(self):
        a = self._eval("window.vb_acao")
        if a in ("ok", "voltar"):
            self._eval("window.vb_acao=''")
            return a
        return None

    def valores(self) -> tuple:
        def ler(id_):
            v = self._eval(f"(function(){{var e=document.getElementById('{id_}'); return e ? e.value : '';}})()")
            return "" if v is None else str(v)
        return tuple(ler(i) for i in ("vb-nome", "vb-idade", "vb-altura", "vb-peso"))

    def mostrar_erro(self, msg: str):
        self._eval(f"(function(){{var e=document.getElementById('vb-erro'); if(e) e.textContent={js_texto(msg)};}})()")

    def fechar(self):
        self._eval(_JS_FECHAR)
