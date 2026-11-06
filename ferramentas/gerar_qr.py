"""Gera o QR code do site para a tela inicial do quiz (só no PC/projetor).

Uso (na pasta do projeto):
    py -m pip install "qrcode[pil]"      # uma vez
    py ferramentas/gerar_qr.py https://viva-bem-seven.vercel.app
"""
import os
import sys

import qrcode

ESCURO, CLARO = "#07161F", "#E8F6F4"   # módulos escuros em fundo claro: lido por qualquer câmera


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    url = sys.argv[1]
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=6, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=ESCURO, back_color=CLARO)
    destino = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "quiz", "assets", "qrcode.png")
    img.save(os.path.normpath(destino))
    print("QR code salvo em", os.path.normpath(destino), "->", url)


if __name__ == "__main__":
    main()
