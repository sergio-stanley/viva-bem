import re

from formulario_web import eh_toque, html_formulario, js_abrir, js_texto


def test_fora_do_navegador_nao_e_toque():
    assert eh_toque() is False


def test_html_tem_os_quatro_campos():
    h = html_formulario()
    for campo in ("vb-nome", "vb-idade", "vb-altura", "vb-peso", "vb-ok", "vb-voltar", "vb-erro"):
        assert f'id="{campo}"' in h


def test_campos_numericos_abrem_teclado_numerico():
    h = html_formulario()
    for campo in ("vb-idade", "vb-altura", "vb-peso"):
        tag = re.search(rf'<input[^>]*id="{campo}"[^>]*>', h).group(0)
        assert 'inputmode="numeric"' in tag and 'maxlength="3"' in tag


def test_nome_limitado_a_20():
    tag = re.search(r'<input[^>]*id="vb-nome"[^>]*>', html_formulario()).group(0)
    assert 'maxlength="20"' in tag and "inputmode" not in tag


def test_fonte_dos_campos_evita_zoom_do_iphone():
    assert "font-size:18px" in html_formulario().replace(" ", "")


def test_js_sem_acentos_crus():
    # acentos crus chegam quebrados pelo platform.window.eval ("formulÃ¡rio")
    js = js_abrir("Altura em centímetros")
    assert js.isascii()
    assert "\\u00ed" in js  # "í" escapado


def test_js_texto_escapa_aspas():
    assert js_texto('a"b') == '"a\\"b"'


def test_navegador_nao_valida_sozinho():
    # a validação é do Python (mensagem clara); o navegador mostraria "formato exigido" e bloquearia o envio
    assert "novalidate" in re.search(r"<form[^>]*>", html_formulario()).group(0)


def test_formulario_segura_as_teclas_antes_do_sdl():
    # o SDL (Pygame no navegador) escuta o teclado na página inteira e chama preventDefault:
    # sem isto, o que a pessoa digita no celular nunca chega aos campos
    js = js_abrir()
    for evento in ("keydown", "keypress", "keyup"):
        assert f"'{evento}'" in js
    assert "stopPropagation" in js


def test_formulario_usa_as_cores_novas_sem_degrade():
    html = html_formulario().lower()
    assert "#10202a" in html and "#eef2f1" in html
    assert "#2dd4bf" not in html and "gradient" not in html
